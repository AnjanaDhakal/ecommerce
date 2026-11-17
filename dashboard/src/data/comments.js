import { createResource } from 'frappe-ui'

const comments = createResource({

    url: '/api/method/ecommerce.api.get_comments',

    auto: true, // required, since it should start fetching automatically
    cache: 'comments',
    method: 'GET',
})


export default comments;
