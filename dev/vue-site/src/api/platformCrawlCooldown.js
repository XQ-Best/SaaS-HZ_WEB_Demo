import { service } from './request'

/** 批量同步结束后写入服务端冷却（子任务 record_cooldown=false 时调用） */
export async function touchPlatformCrawlCooldown() {
  const res = await service.post('/api/platform/crawl-cooldown/touch', {}, {
    skipGlobalErrorToast: true,
  })
  return res?.data ?? res
}
