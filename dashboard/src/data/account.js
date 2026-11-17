import { createResource } from 'frappe-ui'

const account = createResource({

    url: '/api/method/ecommerce.api.get_accounts_summary',

    auto: true, // required, since it should start fetching automatically
    cache: 'account',
    method: 'GET',
})


export default account;
