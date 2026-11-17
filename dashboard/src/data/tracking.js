import { createResource } from 'frappe-ui'

const tracking = createResource({

    url: 'ecommerce.api.track_order',

    auto: true, // required, since it should start fetching automatically
    cache: 'tracking',
    method: 'GET',
})


export default tracking;
