
import { createResource } from 'frappe-ui'

const address = createResource({

    url: '/api/method/ecommerce.api.business_address',

    auto: true, // required, since it should start fetching automatically
    cache: 'address',
    method: 'GET',
})


export default address;
