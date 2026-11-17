import { createResource } from 'frappe-ui'

const deliveryInfo = createResource({

    url: '/api/method/ecommerce.api.get_delivery_amount',

    auto: true, // required, since it should start fetching automatically
    cache: 'delivery-amount',
    method: 'GET',
})


export default deliveryInfo;
