
import { createResource } from 'frappe-ui'

const cancelledorderDetails = createResource({

    url: '/api/method/ecommerce.api.cancelledorder_details',
    auto: true, // required, since it should start fetching automatically
    cache: false, // always fetch fresh data
    method: 'GET',
})


export default cancelledorderDetails;
