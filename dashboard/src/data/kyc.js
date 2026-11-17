
import { createResource } from 'frappe-ui'

const kyc = createResource({

    url: '/api/method/ecommerce.api.get_kyc',

    auto: true, // required, since it should start fetching automatically
    cache: 'kyc',
    method: 'GET',
})


export default kyc;
