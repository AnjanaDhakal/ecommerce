import { createResource } from 'frappe-ui'

const orderDetails = createResource({

    url: '/api/method/ecommerce.api.order_details',

    auto: true, // required, since it should start fetching automatically
    cache: 'order-details',
    method: 'GET',
})


export default orderDetails;
