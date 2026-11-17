import { createResource } from 'frappe-ui'

const discountInfo = createResource({

    url: '/api/method/ecommerce.api.get_delivery_rate',

    auto: true, // required, since it should start fetching automatically
    cache: 'discount-amount',
    method: 'GET',
})


export default discountInfo;
