import { createResource } from 'frappe-ui'

const branch = createResource({

    url: '/api/method/ecommerce.api.get_branches_all',

    auto: true, // required, since it should start fetching automatically
    cache: 'branch',
    method: 'GET',
})


export default branch;
