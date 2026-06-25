import { loadAlibaba1688DemoData } from './alibaba1688DemoLocal'
import { enrichPurchaseOrder, enrichSupplierAlert } from '@/utils/alibaba1688'

export function loadAlibaba1688OperationalData(stores = []) {
  const data = loadAlibaba1688DemoData(stores)
  return {
    success: true,
    data: {
      purchaseOrders: data.purchaseOrders.map(enrichPurchaseOrder),
      supplierAlerts: data.supplierAlerts.map(enrichSupplierAlert),
      syncedAt: new Date().toISOString().replace('T', ' ').slice(0, 19),
    },
  }
}

export function loadAlibaba1688PurchaseOrders(stores = []) {
  const data = loadAlibaba1688DemoData(stores)
  return {
    success: true,
    data: {
      orders: data.purchaseOrders.map(enrichPurchaseOrder),
      syncedAt: new Date().toISOString().replace('T', ' ').slice(0, 19),
    },
  }
}

export function loadAlibaba1688SupplierAlerts(stores = []) {
  const data = loadAlibaba1688DemoData(stores)
  return {
    success: true,
    data: {
      alerts: data.supplierAlerts.map(enrichSupplierAlert),
      syncedAt: new Date().toISOString().replace('T', ' ').slice(0, 19),
    },
  }
}
