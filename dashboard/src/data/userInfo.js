import { createResource } from 'frappe-ui'

const userInfo = createResource({
    url: '/api/method/ecommerce.api.get_user_data',
    auto: true, // required, since it should start fetching automatically
    cache: 'current-user'
})

export default userInfo
