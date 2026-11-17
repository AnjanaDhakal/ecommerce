
import { createResource } from 'frappe-ui'

const editaccount = createResource({

    url: '/api/method/ecommerce.api.get_kyc2',

    auto: true, // required, since it should start fetching automatically
    cache: 'editaccount',
    method: 'GET',
})


export default editaccount;
