/** 平台分类：跨境平台 vs 独立站运营（Shopify / WordPress） */

export const DTC_PLATFORMS = ['shopify', 'wordpress']

export const MARKETPLACE_PLATFORMS = ['temu', 'aliexpress', '1688', 'amazon']

export const PROCUREMENT_PLATFORMS = ['1688']

export const DTC_PLATFORM_OPTIONS = [
  { value: 'shopify', label: 'Shopify' },
  { value: 'wordpress', label: 'WordPress' },
]

export const MARKETPLACE_PLATFORM_OPTIONS = [
  { value: 'temu', label: 'Temu' },
  { value: 'aliexpress', label: 'AliExpress' },
  { value: '1688', label: '1688' },
  { value: 'amazon', label: 'Amazon' },
]

export const OTHER_PLATFORM_OPTIONS = [
  { value: 'tiktok', label: 'TikTok Shop' },
]

export const PLATFORM_OPTION_GROUPS = [
  { label: '跨境平台', options: MARKETPLACE_PLATFORM_OPTIONS },
  { label: '独立站运营', options: DTC_PLATFORM_OPTIONS },
  { label: '其他平台', options: OTHER_PLATFORM_OPTIONS },
]

const DTC_PLATFORM_LABELS = {
  shopify: 'Shopify',
  wordpress: 'WordPress',
}

export function isDtcPlatform(platform) {
  return DTC_PLATFORMS.includes(String(platform || '').trim().toLowerCase())
}

export function dtcPlatformLabel(platform) {
  const key = String(platform || '').trim().toLowerCase()
  return DTC_PLATFORM_LABELS[key] || platform
}
