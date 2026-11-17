import { createResource } from 'frappe-ui';

const ordercount = createResource({
  url: '/api/method/ecommerce.api.vendor_order_count',
  auto: true, // start fetching automatically
  cache: false, // always fetch fresh counts
  method: 'GET',
});

export default ordercount;
