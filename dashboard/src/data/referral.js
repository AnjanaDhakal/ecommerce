
import { createResource } from 'frappe-ui'

const referral = createResource({

    url: '/api/method/ecommerce.api.get_vendor_referral',

    auto: true, // required, since it should start fetching automatically
    cache: 'referral',
    method: 'GET',
})


export default referral;
