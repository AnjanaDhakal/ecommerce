// const API_URL = 'https://dashboard-brown-six-73.vercel.app/api/dashboard'

// const dashboardReport = {
//   data: null,

//   async fetch() {
//     const res = await fetch(API_URL, {
//       method: 'GET',
//     })

//     if (!res.ok) {
//       const body = await res.text().catch(() => '')
//       throw new Error(
//         `Dashboard API failed: ${res.status} ${res.statusText} ${body}`,
//       )
//     }

//     this.data = await res.json()
//     return this.data
//   },
// }

// export default dashboardReport


import { createResource } from 'frappe-ui'

const dashboardReport = createResource({

    url: '/api/method/ecommerce.api.get_all_analytics',

    auto: true,
    cache: 'analytics',
    method: 'GET',
})


export default dashboardReport;
