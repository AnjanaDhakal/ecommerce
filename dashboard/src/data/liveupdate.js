import { createResource } from 'frappe-ui'

const liveupdate = createResource({

    url: '/api/method/ecommerce.api.get_live_updates',

    auto: true, // required, since it should start fetching automatically
    cache: 'live-updates',
    method: 'GET',
})


export default liveupdate;
