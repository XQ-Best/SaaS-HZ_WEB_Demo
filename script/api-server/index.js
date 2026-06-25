import cors from 'cors'
import express from 'express'
import { randomUUID } from 'node:crypto'

const app = express()
const PORT = process.env.PORT || 3000

app.use(cors())
app.use(express.json())

/** @type {Array<{ id: string, platform: string, storeName: string, account: string, companyName?: string, boundAt: string }>} */
const boundStores = []

/** @type {Map<string, string>} storeId -> password */
const credentialVault = new Map()

const ALLOWED_PLATFORMS = ['temu', 'aliexpress']

function normalizePlatform(platform) {
  return String(platform || '').trim().toLowerCase()
}

function publicStore(row) {
  return {
    id: row.id,
    platform: row.platform,
    storeName: row.storeName,
    account: row.account,
    companyName: row.companyName,
    boundAt: row.boundAt,
  }
}

function findStoreIndex(id) {
  return boundStores.findIndex((s) => s.id === id)
}

function validateStoreInput({ platform, storeName, account, password, id }) {
  const p = normalizePlatform(platform)
  if (!ALLOWED_PLATFORMS.includes(p)) {
    return { error: '不支持的平台' }
  }
  const name = String(storeName || '').trim()
  const acc = String(account || '').trim()
  const pwd = String(password || '')

  if (!name) return { error: '店铺名称不能为空' }
  if (!acc) return { error: '登录账号不能为空' }
  if (!id && !pwd) return { error: '登录密码不能为空' }

  const duplicate = boundStores.find(
    (s) => s.platform === p && s.storeName === name && s.id !== id,
  )
  if (duplicate) {
    return { error: `该平台下已存在名为「${name}」的店铺` }
  }

  return { platform: p, storeName: name, account: acc, password: pwd }
}

function upsertStore(payload) {
  const { id, platform, storeName, account, password, companyName } = payload
  const validation = validateStoreInput({ platform, storeName, account, password, id })
  if (validation.error) return { error: validation.error }

  const boundAt = new Date().toISOString()

  if (id) {
    const index = findStoreIndex(id)
    if (index === -1) return { error: '店铺不存在' }
    const existing = boundStores[index]
    if (normalizePlatform(existing.platform) !== validation.platform) {
      return { error: '不允许修改店铺所属平台' }
    }
    boundStores[index] = {
      ...existing,
      storeName: validation.storeName,
      account: validation.account,
      companyName,
      boundAt,
    }
    if (validation.password) {
      credentialVault.set(id, validation.password)
    }
    console.log(`[store-update] ${validation.platform} store=${validation.storeName} account=${validation.account}`)
    return { data: publicStore(boundStores[index]) }
  }

  const newId = randomUUID()
  const row = {
    id: newId,
    platform: validation.platform,
    storeName: validation.storeName,
    account: validation.account,
    companyName,
    boundAt,
  }
  boundStores.push(row)
  credentialVault.set(newId, validation.password)
  console.log(`[store-bind] ${validation.platform} store=${validation.storeName} account=${validation.account}`)
  return { data: publicStore(row) }
}

app.get('/api/health', (_req, res) => {
  res.json({ success: true, message: 'ok' })
})

app.get('/api/platform-accounts', (req, res) => {
  const platform = normalizePlatform(req.query.platform)
  let data = boundStores.map(publicStore)
  if (platform && ALLOWED_PLATFORMS.includes(platform)) {
    data = data.filter((s) => s.platform === platform)
  }
  res.json({ success: true, data })
})

app.post('/api/platform-accounts/bind', (req, res) => {
  const companyName = String(req.body.companyName || '').trim()
  const result = upsertStore({ ...req.body, companyName })
  if (result.error) {
    return res.status(400).json({ success: false, message: result.error })
  }
  res.json({
    success: true,
    message: req.body.id ? '店铺更新成功' : '店铺绑定成功',
    data: result.data,
  })
})

app.post('/api/platform-accounts/bind-batch', (req, res) => {
  const companyName = String(req.body.companyName || '').trim()
  const stores = Array.isArray(req.body.stores) ? req.body.stores : []

  if (!stores.length) {
    return res.status(400).json({ success: false, message: '请至少提交一个店铺' })
  }

  const results = []
  const errors = []

  for (const item of stores) {
    const result = upsertStore({ ...item, companyName })
    if (result.error) {
      errors.push({ storeName: item.storeName, platform: item.platform, message: result.error })
    } else {
      results.push(result.data)
    }
  }

  if (!results.length) {
    return res.status(400).json({ success: false, message: '绑定失败', errors })
  }

  res.json({
    success: true,
    message: `成功绑定/更新 ${results.length} 个店铺`,
    data: results,
    errors: errors.length ? errors : undefined,
  })
})

app.delete('/api/platform-accounts/:id', (req, res) => {
  const index = findStoreIndex(req.params.id)
  if (index === -1) {
    return res.status(404).json({ success: false, message: '店铺不存在' })
  }
  const removed = boundStores.splice(index, 1)[0]
  credentialVault.delete(removed.id)
  console.log(`[store-delete] ${removed.platform} store=${removed.storeName}`)
  res.json({ success: true, message: '店铺已解除绑定', data: publicStore(removed) })
})

app.listen(PORT, () => {
  console.log(`CrossHub API server running at http://localhost:3000`)
})
