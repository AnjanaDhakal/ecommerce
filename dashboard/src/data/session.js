// import router from '@/router'
// import { computed, reactive } from 'vue'
// import { createResource } from 'frappe-ui'

// import { userResource } from './user'

// export function sessionUser() {
//   const cookies = new URLSearchParams(document.cookie.split('; ').join('&'))
//   let _sessionUser = cookies.get('user_id')
//   if (_sessionUser === 'Guest') {
//     _sessionUser = null
//   }
//   return _sessionUser
// }


// function clearBrowserCache() {
//   // Clear localStorage
//   localStorage.clear();

//   // Clear sessionStorage
//   sessionStorage.clear();

//   // Clear IndexedDB
//   const indexedDBDatabases = indexedDB.databases ? indexedDB.databases() : Promise.resolve([]);
//   indexedDBDatabases.then(databases => {
//     databases.forEach(dbInfo => {
//       const request = indexedDB.deleteDatabase(dbInfo.name);
//       request.onsuccess = () => console.log(`Deleted database ${dbInfo.name}`);
//       request.onerror = () => console.log(`Failed to delete database ${dbInfo.name}`);
//     });
//   }).catch(() => {
//     console.warn('Could not list IndexedDB databases.');
//   });
// }

// export const session = reactive({
//   login: createResource({
//     url: 'login',
//     makeParams({ email, password }) {
//       return {
//         usr: email,
//         pwd: password,
//       }
//     },
//     onSuccess(data) {
//       userResource.reload()
//       session.user = sessionUser()
//       session.login.reset()
//       router.replace(data.default_route || '/')
//     },
//   }),
//   logout: createResource({
//     url: 'logout',
//     onSuccess() {
//       clearBrowserCache();
//       userResource.reset()
//       session.user = sessionUser()
//       window.location.href = '/login?redirect-to=/dashboard';
//     },
//   }),

//   user: sessionUser(),
//   isLoggedIn: computed(() => !!session.user),
// })


import router from '@/router'
import { computed, reactive, ref } from 'vue'
import { createResource } from 'frappe-ui'

import { userResource } from './user'
import { loginUrl, sessionUser } from './auth'

const isLoggingOut = ref(false)


function clearBrowserCache() {
  // Clear localStorage
  localStorage.clear();

  // Clear sessionStorage
  sessionStorage.clear();

  // Clear IndexedDB
  const indexedDBDatabases = indexedDB.databases ? indexedDB.databases() : Promise.resolve([]);
  indexedDBDatabases.then(databases => {
    databases.forEach(dbInfo => {
      const request = indexedDB.deleteDatabase(dbInfo.name);
      // request.onsuccess = () => console.log(`Deleted database ${dbInfo.name}`);
      // request.onerror = () => console.log(`Failed to delete database ${dbInfo.name}`);
    });
  }).catch(() => {
    console.warn('Could not list IndexedDB databases.');
  });
}

export const session = reactive({
  login: createResource({
    url: 'login',
    makeParams({ email, password }) {
      return {
        usr: email,
        pwd: password,
      }
    },
    onSuccess() {
      userResource.reload()
      session.user = sessionUser()
      session.login.reset()
      router.replace({ name: 'main' })
    },
  }),
  logout: createResource({
    url: 'logout',
    onStart() {
      isLoggingOut.value = true
    },
    onSuccess() {
      clearBrowserCache()
      userResource.reset()
      session.user = null
      window.location.replace(loginUrl())
    },
    onError(error) {
      console.warn('Logout error:', error)
    },
    onFinish() {
      isLoggingOut.value = false
    },
  }),

  user: sessionUser(),
  isLoggedIn: computed(() => !!session.user),
})
