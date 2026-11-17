import { createResource } from 'frappe-ui';

const openorderDetails = createResource({
  url: '/api/method/ecommerce.api.openorder_details',
  auto: true, // required, since it should start fetching automatically
  cache: false, // always fetch fresh data
  method: 'GET',
});

export default openorderDetails;
