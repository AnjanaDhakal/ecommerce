import { createResource } from 'frappe-ui'

const ticketDetails = createResource({
    url: '/api/method/ecommerce.api.ticket_details',
    auto: true, // required, since it should start fetching automatically
    cache: 'ticekt-details',
    method: 'GET',
})

const createTicket = createResource({
    url: '/api/method/ecommerce.api.create_ticket',
    method: 'POST',
    cache: 'create'
})

export { ticketDetails, createTicket }
