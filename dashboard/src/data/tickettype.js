import { createResource } from 'frappe-ui'

const tickettype = createResource({

    url: '/api/method/ecommerce.api.get_ticket_type',

    auto: true, // required, since it should start fetching automatically
    cache: 'ticket-type',
    method: 'GET',
})


export default tickettype;
