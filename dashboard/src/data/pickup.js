import { createResource } from 'frappe-ui'

const pickup = createResource({

    url: '/api/method/ecommerce.api.ongoing_pickup',

    auto: true, // required, since it should start fetching automatically
    cache: 'ongoing-pickup',
    method: 'GET',
})


export default pickup;
