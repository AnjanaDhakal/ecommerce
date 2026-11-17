<template>
  <div
    class="p-2 mt-1 lg:bg-gray-200 h-[calc(100svh-5.5rem)] lg:h-[calc(100svh-5rem)] overflow-hidden"
  >
    <div
      class="border-gray-200 rounded-lg bg-white h-full overflow-hidden grid grid-cols-1"
      :style="desktopIntegrationGridStyle"
    >
      <div
        class="bg-white text-gray-900 flex flex-col border-r border-gray-200 min-h-0 rounded-l-lg shadow-sm"
        :class="isMobile && !showMenuMobile ? 'hidden' : 'flex'"
      >
        <div
          class="p-4 border-b border-gray-200 flex items-center justify-between"
        >
          <div v-if="!isDesktopCollapsed">
            <p
              class="text-[11px] uppercase tracking-wide text-gray-800 font-semibold"
            >
              Apps
            </p>
            <p class="font-md text-xs"> Marketplace</p>
          </div>
          <button
            v-if="!isMobile"
            type="button"
            class="hidden md:inline-flex h-8 w-8 items-center justify-center rounded-lg text-gray-500 hover:bg-[#f7f7fb] hover:text-gray-800 transition-colors"
            @click="isIntegrationSidebarOpen = !isIntegrationSidebarOpen"
          >
            <img
              :src="sidebarToggleIcon"
              alt="Toggle sidebar"
              class="h-5 w-5 opacity-70"
            />
          </button>
        </div>

        <div v-if="!isDesktopCollapsed" class="p-3">
          <div class="relative">
            <img
              :src="searchIcon"
              alt=""
              class="absolute left-3 top-1/2 h-5 w-5 -translate-y-1/2 text-gray-400 opacity-50"
            />
            <input
              v-model="integrationSearch"
              type="text"
              placeholder="Search integrations"
              class="w-full h-10 px-3 pl-10 text-sm text-gray-800 bg-gray-50 border border-gray-200 focus:outline-none focus:border-[#00a884] rounded-md"
            />
          </div>
        </div>

        <div
          v-if="!isDesktopCollapsed"
          class="pt-1 flex items-center justify-between gap-2"
          :class="appsViewMode === 'grid' ? 'px-3' : 'px-4'"
        >
          <p class="text-[13px] font-semibold text-black/70">Developer Tools</p>

          <div class="flex items-center gap-1 rounded-lg bg-gray-100 p-1">
            <button
              type="button"
              class="h-7 w-7 flex items-center justify-center rounded-md transition-colors"
              :class="
                appsViewMode === 'row'
                  ? 'bg-white text-[#15803d] shadow-sm'
                  : 'text-gray-500 hover:text-gray-800'
              "
              @click="appsViewMode = 'row'"
              title="Row view"
            >
              <span class="material-symbols-outlined text-[18px]"
                >view_list</span
              >
            </button>

            <button
              type="button"
              class="h-7 w-7 flex items-center justify-center rounded-md transition-colors"
              :class="
                appsViewMode === 'grid'
                  ? 'bg-white text-[#15803d] shadow-sm'
                  : 'text-gray-500 hover:text-gray-800'
              "
              @click="appsViewMode = 'grid'"
              title="Grid view"
            >
              <span class="material-symbols-outlined text-[18px]"
                >grid_view</span
              >
            </button>
          </div>
        </div>

        <div
          class="flex-1 overflow-y-auto p-3 pt-2"
          :class="[
            isDesktopCollapsed
              ? 'flex flex-col items-center space-y-1'
              : appsViewMode === 'grid'
                ? 'grid grid-cols-2 content-start gap-x-2 gap-y-2 px-3 pt-2'
                : 'space-y-1',
          ]"
        >
          <template v-for="tab in filteredIntegrationTabs" :key="tab.key">
            <div
              v-if="tab.groupLabel && !isDesktopCollapsed"
              :class="[
                appsViewMode === 'grid' ? 'col-span-2 px-1 pt-2' : 'px-2 pt-2',
              ]"
            >
              <p class="text-[13px] font-semibold text-black/70">
                {{ tab.groupLabel }}
              </p>
            </div>

            <button
              class="w-full text-left flex items-center gap-2 transition-colors"
              :class="{
                'rounded-2xl px-3 py-2': appsViewMode !== 'grid',

                'bg-[#e6f2eb]': isTabVisuallyActive(tab),

                'hover:bg-[#f7f7fb]': !isTabVisuallyActive(tab),

                'justify-center !px-0': isDesktopCollapsed,

                'min-h-[88px] flex-col items-center justify-start gap-1 rounded-xl p-2 text-center':
                  !isDesktopCollapsed && appsViewMode === 'grid',
              }"
              @click="selectTab(tab.key)"
              :title="tab.label"
            >
              <div
                class="relative flex h-8 w-8 shrink-0 items-center justify-center overflow-visible rounded-lg"
                :class="[
                  tab.tileClass,
                  !isDesktopCollapsed &&
                    appsViewMode === 'grid' &&
                    'h-12 w-12 rounded-xl',
                ]"
                :style="tab.tileStyle"
              >
                <img
                  :src="tab.menuIcon"
                  :alt="tab.label"
                  :class="[
                    tab.iconFillsTile
                      ? !isDesktopCollapsed && appsViewMode === 'grid'
                        ? 'h-10 w-10 rounded-lg object-contain'
                        : 'h-7 w-7 rounded-[7px] object-cover'
                      : !isDesktopCollapsed && appsViewMode === 'grid'
                        ? 'h-8 w-8'
                        : 'h-4 w-4',
                    tab.iconClass,
                  ]"
                />
                <img
                  v-if="
                    tab.verified &&
                    !tab.cornerBadge &&
                    !isDesktopCollapsed &&
                    appsViewMode === 'grid'
                  "
                  :src="verifiedBadgeIcon"
                  alt=""
                  class="absolute right-0 top-0 h-5 w-5 translate-x-[34%] -translate-y-[34%] shrink-0 rounded-full bg-white p-[2px]"
                />
                <span
                  v-if="tab.cornerBadge && !isDesktopCollapsed"
                  class="absolute left-0 top-0 translate-x-[-42%] -translate-y-[38%] rounded-[8px] px-1.5 py-0.5 text-[8px] font-bold uppercase tracking-[0.03em] text-white shadow-[0_0_0_2px_white]"
                  :class="tab.cornerBadgeClass"
                >
                  {{ tab.cornerBadge }}
                </span>
              </div>

              <div
                v-if="!isDesktopCollapsed"
                :class="[
                  appsViewMode === 'grid'
                    ? 'flex w-full flex-col items-center text-center gap-0.5'
                    : 'min-w-0 flex-1 space-y-0.5',
                ]"
              >
                <div class="flex items-center gap-1.5">
                  <span
                    class="max-w-full truncate text-sm"
                    :class="
                      isTabVisuallyActive(tab)
                        ? 'font-semibold text-[#15803d]'
                        : 'font-medium text-gray-800'
                    "
                  >
                    {{ tab.label }}
                  </span>
                  <img
                    v-if="tab.verified && appsViewMode !== 'grid'"
                    :src="verifiedBadgeIcon"
                    alt=""
                    class="h-3.5 w-3.5 shrink-0"
                  />
                </div>
                <div
                  v-if="appsViewMode !== 'grid'"
                  class="truncate text-[11px]"
                >
                  {{ tab.menuSubtitle }}
                </div>
              </div>

              <span
                v-if="
                  !isDesktopCollapsed &&
                  tab.menuBadge &&
                  tab.menuBadge !== 'Free'
                "
                :class="[
                  appsViewMode === 'grid'
                    ? 'mt-0.5 bg-[#dcfce7] text-[#15803d] rounded-full px-4 py-1 text-xs font-semibold'
                    : 'shrink-0 rounded-full px-2 py-1 text-[0.6rem] font-bold',
                  isTabVisuallyActive(tab) ? 'bg-white text-[#15803d]' : '',
                ]"
              >
                {{ tab.menuBadge }}
              </span>

              <img
                v-if="!isDesktopCollapsed && appsViewMode !== 'grid'"
                :src="chevronRightIcon"
                alt=""
                class="h-4 w-4 shrink-0"
                :class="isTabVisuallyActive(tab) ? '' : 'opacity-40'"
              />
            </button>
          </template>
        </div>
      </div>

      <div
        class="bg-white flex flex-col overflow-hidden min-h-0 h-full shadow-sm border border-gray-200"
        :class="[
          isMobile && showMenuMobile ? 'hidden' : 'flex',
          'rounded-r-lg border-l-0',
        ]"
      >
        <div
          v-if="!isEcommerceToolOpen || activeTab === 'ecommerce'"
          class="h-14 px-4 flex items-center justify-between border-b border-gray-200 bg-gray-50 gap-3"
        >
          <div class="space-y-0.5">
            <div class="text-sm text-gray-800 flex items-center gap-2">
              <button
                v-if="isMobile"
                class="md:hidden text-gray-600 hover:text-gray-800"
                @click="showMenuMobile = true"
              >
                <span class="material-symbols-outlined text-lg"
                  >arrow_back</span
                >
              </button>
              <span>{{ activeTabMeta.title }}</span>
            </div>
            <div class="text-sm text-gray-500">
              {{ activeTabMeta.subtitle }}
            </div>
          </div>

          <div class="flex shrink-0 items-center gap-2">
            <Switch
              v-if="activeTab === 'ecommerce'"
              size="sm"
              :model-value="isEcommerceEnabled"
              :label="
                ecommerceFeatureSaving
                  ? 'Updating…'
                  : isEcommerceEnabled
                    ? 'Enabled'
                    : 'Disabled'
              "
              :disabled="ecommerceFeatureSaving"
              @update:modelValue="updateEcommerceFeature"
            />
            <div
              v-if="activeTab === 'ecommerce'"
              class="h-9 w-9 overflow-hidden rounded-lg"
            >
              <img
                :src="ecommerceIcon"
                alt=""
                class="h-full w-full object-cover"
              />
            </div>
            <Button
              v-if="activeTab === 'api'"
              variant="solid"
              @click="goToApiDetails"
            >
              View Documentation
            </Button>
          </div>
        </div>

        <div
          class="flex-1 min-h-0 bg-gray-50"
          :class="
            activeTab === 'ecommerce'
              ? 'overflow-hidden p-0'
              : 'overflow-y-auto p-4'
          "
        >
          <div
            class="bg-white"
            :class="
              activeTab === 'ecommerce'
                ? 'h-full min-h-0 p-4'
                : 'rounded-lg border border-gray-200 p-4 sm:p-5'
            "
          >
            <div
              v-if="!isEcommerceToolOpen && activeTab !== 'ecommerce'"
              class="flex items-start justify-between gap-4 mb-4"
            >
              <div>
                <img
                  v-if="activeTabMeta.eyebrowIcon"
                  :src="activeTabMeta.eyebrowIcon"
                  :alt="`${activeTabMeta.eyebrow} icon`"
                  class="h-10 w-12 object-contain object-left"
                />
                <p
                  v-else
                  class="text-xs font-semibold uppercase tracking-wide text-gray-500"
                >
                  {{ activeTabMeta.eyebrow }}
                </p>
                <h2 class="text-xl font-semibold text-gray-900 mt-1">
                  {{ activeTabMeta.heading }}
                </h2>
                <p class="text-sm text-gray-600 mt-2 max-w-3xl">
                  {{ activeTabMeta.description }}
                </p>
              </div>
              <div
                class="h-11 w-11 rounded-xl border border-gray-200 flex items-center justify-center shrink-0 overflow-hidden"
                :class="activeTabMeta.tileClass"
                :style="activeTabMeta.tileStyle"
              >
                <img
                  :src="activeTabMeta.menuIcon"
                  :alt="activeTabMeta.label"
                  :class="[
                    activeTabMeta.iconFillsTile
                      ? 'h-9 w-9 rounded-[10px] object-cover'
                      : 'h-5 w-5',
                    activeTabMeta.iconClass,
                  ]"
                />
              </div>
            </div>

            <div v-if="activeTab === 'api'" class="space-y-4">
              <div class="grid gap-4 xl:grid-cols-2">
                <div class="rounded-lg border border-gray-200 bg-gray-50 p-4">
                  <h3 class="text-sm font-semibold text-gray-900 mb-3">
                    Demo Server Login Details
                  </h3>
                  <div class="space-y-2 text-sm text-gray-700 break-all">
                    <div>
                      Url:
                      <a
                        target="_blank"
                        href="https://app-t.pickndropnepal.com/login"
                        class="font-semibold text-blue-600 hover:text-blue-700"
                      >
                        https://app-t.pickndropnepal.com/login
                      </a>
                    </div>
                    <div>
                      Base URL:
                      <strong>https://app-t.pickndropnepal.com</strong>
                    </div>
                    <div>Email: <strong>demo@user.test</strong></div>
                    <div>Password: <strong>Demo@1234</strong></div>
                    <div>Demo API Key: <strong>bf1a7ce75dacf51</strong></div>
                    <div>Demo API Secret: <strong>63b8931e70aee27</strong></div>
                  </div>
                </div>

                <div class="rounded-lg border border-gray-200 bg-gray-50 p-4">
                  <h3 class="text-sm font-semibold text-gray-900 mb-3">
                    Production Access
                  </h3>
                  <p class="text-sm text-gray-600 mb-4">
                    Generate production credentials after validating your
                    implementation on the demo environment.
                  </p>
                  <Button variant="solid" @click="generateApiKeys">
                    {{ apiKey ? 'Generate API Secret' : 'Generate API Key' }}
                  </Button>

                  <div v-if="apiKey" class="mt-4 space-y-3">
                    <div>
                      <p
                        class="text-xs font-semibold uppercase tracking-wide text-gray-500 mb-1"
                      >
                        API Key
                      </p>
                      <TextInput
                        type="text"
                        size="sm"
                        variant="subtle"
                        v-model="apiKey"
                        readonly
                        class="bg-white"
                      />
                    </div>
                    <div>
                      <p
                        class="text-xs font-semibold uppercase tracking-wide text-gray-500 mb-1"
                      >
                        API Secret
                      </p>
                      <TextInput
                        type="password"
                        size="sm"
                        variant="subtle"
                        placeholder="Shown once in dialog"
                        readonly
                        class="bg-white"
                      />
                    </div>
                  </div>
                </div>
              </div>

              <div
                class="rounded-lg border border-gray-200 bg-gray-50 p-4 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between"
              >
                <div>
                  <h3 class="text-sm font-semibold text-gray-900">
                    API Documentation
                  </h3>
                  <p class="text-sm text-gray-600 mt-1">
                    Review endpoints, payloads, and authentication before moving
                    to production.
                  </p>
                </div>
                <a
                  href="https://pickndrop.apidog.io/"
                  target="_blank"
                  class="inline-flex items-center justify-center rounded-lg bg-green-600 px-4 py-2 text-sm font-semibold text-white hover:bg-green-700"
                >
                  Go to API Documentation
                </a>
              </div>

              <div class="rounded-lg border border-gray-200 bg-gray-50 p-4">
                <h3 class="text-sm font-semibold text-gray-900">Support</h3>
                <p class="text-sm text-gray-600 mt-1">
                  Contact
                  <a
                    href="mailto:developer@pickndropnepal.com"
                    class="text-blue-600 hover:text-blue-700"
                  >
                    developer@pickndropnepal.com
                  </a>
                  for integration help.
                </p>
              </div>
            </div>

            <div v-else-if="activeTab === 'webhook'" class="space-y-4">
              <div
                class="rounded-lg border border-gray-200 bg-gray-50 p-4 flex items-start justify-between gap-4"
              >
                <div>
                  <h3 class="text-sm font-semibold text-gray-900">
                    Connection Status
                  </h3>
                  <p class="text-sm text-gray-600 mt-1">
                    Receive package status and comment updates in your own
                    system.
                  </p>
                </div>
                <div
                  class="inline-flex items-center gap-2 rounded-full px-3 py-1 text-xs font-semibold"
                  :class="
                    enablewebhook === 1
                      ? 'bg-green-100 text-green-700'
                      : 'bg-gray-100 text-gray-600'
                  "
                >
                  <span
                    class="inline-block h-2.5 w-2.5 rounded-full"
                    :class="
                      enablewebhook === 1 ? 'bg-green-500' : 'bg-gray-400'
                    "
                  ></span>
                  {{ enablewebhook === 1 ? 'Connected' : 'Not Connected' }}
                </div>
              </div>

              <div class="grid gap-4 xl:grid-cols-2">
                <div class="rounded-lg border border-gray-200 bg-gray-50 p-4">
                  <h3 class="text-sm font-semibold text-gray-900 mb-4">
                    Status Change Event Webhook
                  </h3>

                  <div class="flex items-center space-x-2 mb-4">
                    <Switch
                      size="sm"
                      :label="isWebhookEnabled ? 'Enabled' : 'Disabled'"
                      v-model="isWebhookEnabled"
                      @update:modelValue="handleStatusToggle"
                      :disabled="!isFeatureEnabled"
                    />
                  </div>

                  <div
                    class="grid gap-4 lg:grid-cols-[140px_minmax(0,1fr)] lg:items-center mb-4"
                  >
                    <p class="text-sm font-medium text-gray-800">
                      Base URL<span class="text-red-700 text-lg">*</span>
                    </p>
                    <TextInput
                      type="text"
                      size="sm"
                      variant="subtle"
                      v-model="request_url"
                      placeholder="https://example.com"
                      class="bg-white hover:bg-white"
                    />
                  </div>

                  <div
                    class="grid gap-4 lg:grid-cols-[140px_minmax(0,1fr)] lg:items-center mb-6"
                  >
                    <p class="text-sm font-medium text-gray-800">
                      Webhook Secret<span class="text-red-700 text-lg">*</span>
                    </p>
                    <TextInput
                      type="password"
                      size="sm"
                      variant="subtle"
                      v-model="webhookKey"
                      placeholder="Enter webhook secret"
                      class="bg-white hover:bg-white"
                    />
                  </div>

                  <Button variant="solid" @click="handleConnect">Save</Button>

                  <p v-if="message" class="mt-3 text-sm text-gray-700">
                    {{ message }}
                  </p>
                  <p v-if="error" class="mt-3 text-sm text-red-700">
                    {{ error }}
                  </p>
                </div>

                <div class="rounded-lg border border-gray-200 bg-gray-50 p-4">
                  <div class="flex items-start justify-between gap-3 mb-4">
                    <div>
                      <h3 class="text-sm font-semibold text-gray-900">
                        Sandbox
                      </h3>
                      <p class="mt-1 text-sm text-gray-600">
                        Send a test webhook request with `orderID` and `status`.
                      </p>
                    </div>
                    <span
                      class="rounded-full bg-amber-100 px-2.5 py-1 text-[11px] font-semibold text-amber-700"
                    >
                      Test
                    </span>
                  </div>

                  <div class="space-y-4">
                    <div
                      class="grid gap-4 lg:grid-cols-[100px_minmax(0,1fr)] lg:items-center"
                    >
                      <p class="text-sm font-medium text-gray-800">
                        Order ID<span class="text-red-700 text-lg">*</span>
                      </p>
                      <TextInput
                        type="text"
                        size="sm"
                        variant="subtle"
                        v-model="sandboxOrderId"
                        placeholder="XYZ-123"
                        class="bg-white hover:bg-white"
                      />
                    </div>

                    <div
                      class="grid gap-4 lg:grid-cols-[100px_minmax(0,1fr)] lg:items-center"
                    >
                      <p class="text-sm font-medium text-gray-800">
                        Status<span class="text-red-700 text-lg">*</span>
                      </p>
                      <select
                        v-model="sandboxStatus"
                        class="h-9 w-full rounded-md border border-gray-200 bg-white px-3 text-sm text-gray-800 outline-none focus:border-[#00a884]"
                      >
                        <option disabled value="">Select status</option>
                        <option
                          v-for="option in sandboxStatusOptions"
                          :key="option.value"
                          :value="option.value"
                        >
                          {{ option.label }}
                        </option>
                      </select>
                    </div>
                  </div>

                  <div class="mt-6 flex items-center gap-3">
                    <Button
                      variant="solid"
                      @click="sendWebhookSandbox"
                      :loading="sandboxLoading"
                    >
                      Send Sandbox Request
                    </Button>
                  </div>

                  <p v-if="sandboxMessage" class="mt-3 text-sm text-gray-700">
                    {{ sandboxMessage }}
                  </p>
                  <p v-if="sandboxError" class="mt-3 text-sm text-red-700">
                    {{ sandboxError }}
                  </p>

                  <div
                    v-if="showSandboxDemoDetails"
                    class="mt-4 rounded-md border border-amber-200 bg-amber-50 p-4 text-sm text-gray-700"
                  >
                    <h4 class="font-semibold text-gray-900">
                      Demo Server Login Details
                    </h4>
                    <div class="mt-2 space-y-1 break-all">
                      <p>
                        Url:
                        <a
                          href="https://app-t.pickndropnepal.com/login"
                          target="_blank"
                          rel="noopener noreferrer"
                          class="font-semibold text-blue-600 hover:text-blue-700"
                        >
                          https://app-t.pickndropnepal.com/login
                        </a>
                      </p>
                      <p>
                        Base URL:
                        <strong>https://app-t.pickndropnepal.com</strong>
                      </p>
                      <p>Email: <strong>demo@user.test</strong></p>
                      <p>Password: <strong>Demo@1234</strong></p>
                      <p>Demo API Key: <strong>bf1a7ce75dacf51</strong></p>
                      <p>
                        Demo API Secret:
                        <strong>63b8931e70aee27</strong>
                      </p>
                    </div>
                    <p class="mt-3 font-medium text-amber-800">
                      Use this demo server for sandbox testing.
                    </p>
                  </div>

                  <div
                    v-if="sandboxResponse"
                    class="mt-4 overflow-x-auto rounded-md border border-gray-200 bg-white p-3"
                  >
                    <pre class="text-xs text-gray-700 whitespace-pre-wrap">{{
                      sandboxResponse
                    }}</pre>
                  </div>
                </div>
              </div>

              <div class="rounded-lg border border-gray-200 bg-gray-50 p-4">
                <h3 class="text-sm font-semibold text-gray-900 mb-2">
                  Webhook Payload
                </h3>
                <div class="border rounded-md p-3 bg-white overflow-x-auto">
                  <pre class="text-sm text-gray-700 whitespace-pre-wrap">
{
  "orderID": "XYZ-123",
  "comments": "Customer cancel before Delivery",
  "epod": "",
  "package_type": "Regular",
  "status": "return_at_transit_hub",
  "timestamp": "08-18-2025 13:13:15",
  "tracking_number": "PND-NP-000566118"
}</pre
                  >
                </div>
              </div>

              <div
                class="rounded-lg border border-gray-200 bg-gray-50 p-4 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between"
              >
                <div>
                  <h3 class="text-sm font-semibold text-gray-900">
                    Webhook Documentation
                  </h3>
                  <p class="text-sm text-gray-600 mt-1">
                    Review the webhook contract and event format before going
                    live.
                  </p>
                </div>
                <a
                  href="https://pickndrop.apidog.io/-pick-drop-webhook-integration-1375447m0"
                  target="_blank"
                  class="inline-flex items-center justify-center rounded-lg bg-green-600 px-4 py-2 text-sm font-semibold text-white hover:bg-green-700"
                >
                  Go to Webhook Documentation
                </a>
              </div>
            </div>

            <div
              v-else-if="
                activeTab === 'sparrow-sms' || activeTab === 'aakash-sms'
              "
              class="space-y-4"
            >
              <div class="rounded-lg border border-gray-200 bg-gray-50 p-4">
                <div class="flex items-start justify-between gap-4">
                  <div>
                    <h3 class="text-sm font-semibold text-gray-900">
                      {{
                        activeTab === 'sparrow-sms'
                          ? 'Sparrow SMS'
                          : 'Aakash SMS'
                      }}
                      Gateway
                    </h3>
                    <p class="mt-1 text-sm text-gray-600">
                      Configure your SMS gateway to send OTP, delivery, and
                      status notification messages.
                    </p>
                  </div>
                  <span
                    class="rounded-full bg-green-100 px-2 py-1 text-xs font-semibold text-green-700"
                  >
                    NEW
                  </span>
                </div>
              </div>

              <div class="rounded-lg border border-gray-200 bg-gray-50 p-4">
                <h3 class="mb-2 text-sm font-semibold text-gray-900">
                  Coming Next
                </h3>
                <p class="mb-4 text-sm text-gray-600">
                  Provider credentials, sender configuration, and test message
                  flows will be available from this app panel.
                </p>
                <Button variant="solid" disabled> Setup SMS Gateway </Button>
              </div>
            </div>

            <div
              v-else-if="activeTab === 'ecommerce' && ecommerceFeatureLoading"
              class="flex h-full min-h-[24rem] items-center justify-center"
            >
              <div class="text-center">
                <span
                  class="material-symbols-outlined animate-spin text-3xl text-gray-400"
                >
                  progress_activity
                </span>
                <p class="mt-2 text-sm text-gray-500">
                  Checking ECommerce availability…
                </p>
              </div>
            </div>

            <div
              v-else-if="activeTab === 'ecommerce' && !isEcommerceEnabled"
              class="flex h-full min-h-[24rem] items-center justify-center p-4"
            >
              <div
                class="w-full max-w-xl rounded-2xl border border-gray-200 bg-white p-8 text-center shadow-sm"
              >
                <div
                  class="mx-auto flex h-16 w-16 items-center justify-center overflow-hidden rounded-2xl bg-orange-50"
                >
                  <img
                    :src="ecommerceIcon"
                    alt=""
                    class="h-14 w-14 object-contain"
                  />
                </div>
                <p
                  class="mt-5 text-xs font-bold uppercase tracking-[0.14em] text-emerald-700"
                >
                  Optional app
                </p>
                <h2 class="mt-2 text-2xl font-semibold text-gray-900">
                  Enable ECommerce
                </h2>
                <p class="mx-auto mt-3 max-w-md text-sm leading-6 text-gray-600">
                  ECommerce is disabled by default. Enable it to create a
                  storefront, manage products, and process online orders.
                </p>
                <p
                  v-if="ecommerceFeatureError"
                  class="mt-4 rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700"
                >
                  {{ ecommerceFeatureError }}
                </p>
                <Button
                  class="mt-6"
                  variant="solid"
                  :loading="ecommerceFeatureSaving"
                  @click="updateEcommerceFeature(true)"
                >
                  Enable ECommerce
                </Button>
              </div>
            </div>

            <div
              v-else-if="activeTab === 'ecommerce'"
              class="grid h-full min-h-0 grid-rows-[auto_minmax(0,1fr)] items-stretch gap-4 md:grid-cols-[13rem_minmax(0,1fr)] md:grid-rows-1"
            >
              <EcommerceToolNavigation
                v-model="ecommerceMenuValue"
                class="md:h-full"
              />

              <div
                :key="ecommerceMenuValue"
                class="ecommerce-content-panel min-h-0 min-w-0"
                :class="[
                  isEcommerceCollectionTool
                    ? 'overflow-hidden'
                    : 'overflow-y-auto',
                  selectedEcommerceTool === 'analytics' ? 'px-1 pb-4' : '',
                ]"
              >
                <template v-if="!selectedEcommerceTool">
                  <EcommerceWebsiteOverview />
                </template>

                <div
                  v-else
                  class="min-w-0"
                  :class="
                    isEcommerceCollectionTool
                      ? 'flex h-full min-h-0 flex-col'
                      : ''
                  "
                >
                  <div class="mb-4 flex items-center justify-between gap-3 border-b border-gray-200 pb-3">
                    <h2 class="text-lg font-semibold text-gray-900">
                      {{ selectedEcommerceToolMeta.label }}
                    </h2>
                  </div>

                  <component
                    :is="selectedEcommerceComponent"
                    embedded
                    :class="isEcommerceCollectionTool ? 'min-h-0 flex-1' : ''"
                  />
                </div>
              </div>
            </div>

            <div v-else-if="activeTab === 'mcp-server'" class="space-y-5">
              <div
                class="rounded-xl border border-[#1e293b] bg-[#f9fafc] px-5 py-4"
              >
                <div
                  class="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between"
                >
                  <div class="min-w-0 flex-1">
                    <p
                      class="text-[10px] font-semibold uppercase tracking-[0.12em] text-black"
                    >
                      MCP Endpoint
                    </p>
                    <p
                      class="mt-1 break-all font-mono text-sm font-semibold text-black"
                    >
                      {{ mcpEndpoint }}
                    </p>
                  </div>
                  <div class="flex flex-wrap items-center gap-3">
                    <span
                      class="inline-flex items-center gap-2 rounded-full border border-[#334155] px-3 py-1.5 text-xs font-medium text-black"
                    >
                      <span class="material-symbols-outlined text-sm"
                        >lock</span
                      >
                      OAuth required
                    </span>
                    <button
                      type="button"
                      class="rounded-lg bg-[#16a34a] px-4 py-2 text-sm font-semibold text-white transition-colors hover:bg-[#15803d]"
                      @click="copyMcpEndpoint"
                    >
                      {{ mcpEndpointCopied ? 'Copied' : 'Copy' }}
                    </button>
                  </div>
                </div>
              </div>

              <div class="flex flex-col gap-5 xl:flex-row">
                <div class="min-w-0 flex-[2] space-y-5">
                  <div
                    class="rounded-xl border border-gray-200 bg-white p-5 shadow-sm"
                  >
                    <div
                      class="flex flex-col gap-2 sm:flex-row sm:items-baseline sm:justify-between"
                    >
                      <h3 class="text-sm font-semibold text-gray-900">
                        Configuration
                      </h3>
                      <p class="text-xs text-gray-500">
                        Add the server to your client's MCP config.
                      </p>
                    </div>

                    <div
                      class="mt-4 inline-flex flex-wrap gap-2 rounded-xl bg-slate-100 p-1"
                    >
                      <button
                        v-for="tab in mcpClientTabs"
                        :key="tab.key"
                        type="button"
                        class="rounded-lg border px-3 py-1.5 text-sm transition-colors"
                        :class="
                          mcpClientTab === tab.key
                            ? 'border-gray-200 bg-white font-semibold text-slate-900 shadow-sm'
                            : 'border-transparent font-medium text-slate-500 hover:text-slate-900'
                        "
                        @click="mcpClientTab = tab.key"
                      >
                        {{ tab.label }}
                      </button>
                    </div>

                    <div
                      class="mt-4 overflow-hidden rounded-xl border border-slate-200 bg-slate-50"
                    >
                      <div
                        class="flex items-center justify-between gap-3 border-b border-black/10 px-4 py-2.5"
                      >
                        <span class="font-mono text-[11.5px] text-slate-600">
                          {{ activeMcpConfigLabel }}
                        </span>
                        <button
                          type="button"
                          class="rounded-md border border-black/20 px-3 py-1 text-xs font-medium text-slate-700 transition-colors hover:border-[#7c3aed] hover:text-[#6d28d9]"
                          @click="copyMcpConfig"
                        >
                          {{ mcpConfigCopied ? 'Copied' : 'Copy' }}
                        </button>
                      </div>
                      <pre
                        class="overflow-x-auto px-5 py-4 font-mono text-sm leading-6 text-black"
                        >{{ activeMcpConfig }}</pre
                      >
                    </div>

                    <p class="mt-3 text-sm text-gray-500">
                      Works with any MCP-compatible client. OAuth sign-in is
                      prompted on first connection.
                    </p>
                  </div>

                  <div
                    class="rounded-xl border border-gray-200 bg-white p-5 shadow-sm"
                  >
                    <div
                      class="flex flex-col gap-2 sm:flex-row sm:items-baseline sm:justify-between"
                    >
                      <h3 class="text-sm font-semibold text-gray-900">
                        How it works
                      </h3>
                      <button
                        type="button"
                        class="inline-flex items-center gap-1 rounded-full border border-gray-200 px-3 py-1 text-xs font-semibold text-[#15803d] transition-colors hover:border-[#86efac] hover:bg-[#f0fdf4]"
                        @click="toggleMcpFlowPlayback"
                      >
                        <span class="material-symbols-outlined text-sm">
                          {{ mcpFlowPlaying ? 'pause' : 'play_arrow' }}
                        </span>
                        {{ mcpFlowPlaying ? 'Pause' : 'Play' }}
                      </button>
                    </div>

                    <div class="mt-5 space-y-4">
                      <div
                        v-for="(step, index) in mcpFlowSteps"
                        :key="step.label"
                        class="flex cursor-pointer items-start gap-4 pb-1"
                        @click="setMcpFlowStep(index)"
                      >
                        <div
                          class="flex shrink-0 flex-col items-center self-stretch"
                        >
                          <span
                            class="flex h-[26px] w-[26px] items-center justify-center rounded-full border text-xs font-semibold transition-all"
                            :class="
                              index === mcpActiveStep
                                ? 'scale-[1.08] border-[#16a34a] bg-[#16a34a] text-white shadow-[0_0_0_5px_rgba(22,163,74,0.16)]'
                                : index < mcpActiveStep
                                  ? 'border-[#16a34a] bg-[#16a34a] text-white'
                                  : 'border-[#bbf7d0] bg-[#f0fdf4] text-[#86c69a]'
                            "
                          >
                            <span
                              v-if="index < mcpActiveStep"
                              class="material-symbols-outlined text-[13px]"
                            >
                              check
                            </span>
                            <span v-else>{{ index + 1 }}</span>
                          </span>
                          <span
                            v-if="index < mcpFlowSteps.length - 1"
                            class="relative mt-1 min-h-5 w-0.5 flex-1 overflow-hidden rounded bg-slate-100"
                          >
                            <span
                              class="absolute left-0 top-0 w-full bg-[#16a34a] transition-all duration-500"
                              :style="{
                                height: index < mcpActiveStep ? '100%' : '0%',
                              }"
                            />
                          </span>
                        </div>
                        <p
                          class="mt-0.5 text-sm leading-6 transition-colors"
                          :class="
                            index === mcpActiveStep
                              ? 'font-semibold text-gray-900'
                              : index < mcpActiveStep
                                ? 'font-normal text-gray-700'
                                : 'font-normal text-gray-400'
                          "
                        >
                          {{ step.label }}
                        </p>
                      </div>
                    </div>
                  </div>

                  <div
                    class="rounded-xl border border-gray-200 bg-white p-5 shadow-sm"
                  >
                    <h3 class="text-sm font-semibold text-gray-900">
                      Features
                    </h3>
                    <div
                      class="mt-4 grid gap-x-5 gap-y-3 sm:grid-cols-2 xl:grid-cols-3"
                    >
                      <div
                        v-for="feature in mcpFeatures"
                        :key="feature"
                        class="flex items-start gap-2"
                      >
                        <span
                          class="material-symbols-outlined mt-0.5 text-base text-emerald-600"
                        >
                          check
                        </span>
                        <span class="text-sm text-gray-700">{{ feature }}</span>
                      </div>
                    </div>
                  </div>
                </div>

                <div
                  v-if="!isMobile"
                  class="min-w-0 flex-1 space-y-5 xl:max-w-[320px]"
                >
                  <div
                    class="rounded-xl border border-gray-200 bg-white p-5 shadow-sm"
                  >
                    <h3
                      class="mb-2 text-[11px] font-semibold uppercase tracking-[0.08em] text-gray-500"
                    >
                      About
                    </h3>
                    <p class="text-sm leading-6 text-gray-600">
                      The Pick &amp; Drop MCP Server allows AI assistants and
                      MCP-compatible clients to securely interact with the Pick
                      &amp; Drop Nepal platform.
                    </p>
                  </div>

                  <div
                    class="rounded-xl border border-gray-200 bg-white p-5 shadow-sm"
                  >
                    <h3
                      class="mb-3 text-[11px] font-semibold uppercase tracking-[0.08em] text-gray-500"
                    >
                      Available tools
                    </h3>
                    <div class="flex flex-wrap gap-2">
                      <span
                        v-for="tool in mcpTools"
                        :key="tool"
                        class="rounded-lg border border-[#bbf7d0] bg-[#f0fdf4] px-2.5 py-1 font-mono text-xs text-[#15803d]"
                      >
                        {{ tool }}
                      </span>
                    </div>
                  </div>

                  <div
                    class="rounded-xl border border-gray-200 bg-white p-5 shadow-sm"
                  >
                    <h3
                      class="mb-3 text-[11px] font-semibold uppercase tracking-[0.08em] text-gray-500"
                    >
                      Supported clients
                    </h3>
                    <div class="flex flex-wrap gap-2">
                      <span
                        v-for="client in mcpSupportedClients"
                        :key="client"
                        class="rounded-full border border-slate-200 bg-slate-50 px-3 py-1 text-xs font-medium text-slate-700"
                      >
                        {{ client }}
                      </span>
                    </div>
                  </div>

                  <div
                    class="rounded-xl border border-gray-200 bg-white p-5 shadow-sm"
                  >
                    <div class="mb-2 flex items-center gap-2">
                      <span
                        class="material-symbols-outlined text-sm text-[#16a34a]"
                      >
                        lock
                      </span>
                      <h3
                        class="text-[11px] font-semibold uppercase tracking-[0.08em] text-gray-500"
                      >
                        Authentication
                      </h3>
                    </div>
                    <p class="text-sm leading-6 text-gray-600">
                      OAuth-based authentication is required before invoking
                      tools. Your client opens a sign-in window on first
                      connection.
                    </p>
                  </div>
                </div>
              </div>
            </div>

            <div v-else class="space-y-4">
              <div class="rounded-lg border border-gray-200 bg-gray-50 p-4">
                <div class="flex items-start justify-between gap-4">
                  <div>
                    <h3 class="text-sm font-semibold text-gray-900">
                      {{
                        activeTab === 'messenger' ? 'Messenger' : 'Instagram'
                      }}
                      Connection
                    </h3>
                    <p class="text-sm text-gray-600 mt-1">
                      {{
                        activeTab === 'messenger'
                          ? 'Connect Facebook Messenger pages for chat automation and support.'
                          : 'Connect Instagram professional accounts linked to your Facebook business setup.'
                      }}
                    </p>
                  </div>
                  <span
                    class="rounded-full bg-green-100 text-green-700 text-xs font-semibold px-2 py-1"
                  >
                    NEW
                  </span>
                </div>

                <div
                  class="mt-4 flex flex-col gap-3 lg:flex-row lg:items-center lg:justify-between"
                >
                  <Button
                    variant="solid"
                    :disabled="metaConnectionLoading"
                    @click="
                      activeTab === 'messenger'
                        ? connectToMessenger()
                        : connectToInstagram()
                    "
                  >
                    {{
                      metaConnectionLoading
                        ? 'Opening Meta...'
                        : activeTab === 'messenger'
                          ? 'Connect Messenger'
                          : 'Connect Instagram'
                    }}
                  </Button>

                  <div class="w-full lg:w-72">
                    <select
                      v-if="filteredPages.length > 0"
                      v-model="selectedPlatformPageId"
                      @change="handlePageSelection(activePlatform)"
                      class="w-full border border-gray-300 bg-white px-4 py-2 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm text-gray-800"
                    >
                      <option disabled value="">
                        {{
                          selectedPlatformPageName ||
                          `Select ${activeTab === 'messenger' ? 'Messenger' : 'Instagram'} Page`
                        }}
                      </option>
                      <option
                        v-for="pageItem in filteredPages"
                        :key="pageItem.id"
                        :value="pageItem.id"
                      >
                        {{ pageItem.name }}
                      </option>
                    </select>

                    <p
                      v-else
                      class="text-gray-900 flex items-center text-xs font-semibold"
                    >
                      Not Connected
                      <span
                        class="inline-block w-3 h-3 rounded-full bg-gray-400 ml-1"
                      ></span>
                    </p>
                  </div>
                </div>
              </div>

              <div class="rounded-lg border border-gray-200 bg-gray-50 p-4">
                <h3 class="text-sm font-semibold text-gray-900 mb-2">
                  Benefits
                </h3>
                <ul class="space-y-2 text-sm text-gray-600">
                  <li>
                    {{
                      activeTab === 'messenger'
                        ? 'Instant order capture from Messenger conversations.'
                        : 'Connect your Instagram professional inbox to your support flow.'
                    }}
                  </li>
                  <li>
                    {{
                      activeTab === 'messenger'
                        ? 'Reduce manual order entry and avoid operator mistakes.'
                        : 'Route Instagram conversations through the same business setup used for Facebook.'
                    }}
                  </li>
                  <li>
                    {{
                      activeTab === 'messenger'
                        ? 'Track page-level connection status from the selected page list.'
                        : 'Manage connected Instagram pages from the integrated selector.'
                    }}
                  </li>
                </ul>
              </div>

              <div class="rounded-lg border border-gray-200 bg-gray-50 p-4">
                <h3 class="text-sm font-semibold text-gray-900 mb-2">
                  How It Works
                </h3>
                <ol class="list-decimal pl-5 space-y-2 text-sm text-gray-600">
                  <li>
                    Authorize your
                    {{
                      activeTab === 'messenger'
                        ? 'Facebook page'
                        : 'Instagram business account'
                    }}.
                  </li>
                  <li>
                    Select the connected
                    {{
                      activeTab === 'messenger'
                        ? 'Messenger page'
                        : 'Instagram page'
                    }}
                    from the dropdown.
                  </li>
                  <li>
                    Start using the connected channel for
                    {{
                      activeTab === 'messenger'
                        ? 'order capture, customer support, and automation.'
                        : 'messaging, support, and connected business workflows.'
                    }}
                  </li>
                </ol>
              </div>

              <div class="rounded-lg border border-gray-200 bg-gray-50 p-4">
                <h3 class="text-sm font-semibold text-gray-900 mb-2">
                  {{
                    activeTab === 'messenger'
                      ? 'Messenger Bot Overview'
                      : 'Instagram Integration Overview'
                  }}
                </h3>
                <p class="text-sm text-gray-600 mb-4">
                  {{
                    activeTab === 'messenger'
                      ? 'Automate order creation from Facebook Messenger and streamline your support workflow without leaving the Pick & Drop portal.'
                      : 'Review the Instagram connection flow and business account setup directly from the integration page.'
                  }}
                </p>
                <div
                  class="overflow-hidden rounded-lg border border-gray-200 bg-black"
                >
                  <video class="w-full h-auto" controls>
                    <source
                      src="https://pickndropnepal.com/files/facebook-integration.mp4"
                      type="video/mp4"
                    />
                    Your browser does not support the video tag.
                  </video>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>

  <Dialog v-model="dialog2">
    <template #body-title>
      <h3>{{ dialogTitle }}</h3>
    </template>
    <template #body-content>
      <p>{{ dialogMessage }}</p>
    </template>
  </Dialog>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Button, Dialog, Switch, TextInput } from 'frappe-ui'
import EcommerceToolNavigation from '../components/EcommerceToolNavigation.vue'
import { PanelLeft } from 'lucide-vue-next'
import { useSidebar } from '@/components/ui/sidebar'
import {
  SIDEBAR_WIDTH,
  SIDEBAR_WIDTH_ICON,
} from '@/components/ui/sidebar/utils'
import page from '../data/apipage'
import webhook from '../data/webhook'
import EcommerceAnalytics from '@/components/EcommerceAnalytics.vue'
import EcommerceBrands from '@/components/Brands.vue'
import EcommerceCategories from '@/components/Catagories.vue'
import EcommerceAddProduct from '@/components/AddProduct.vue'
import EcommerceOrders from '@/components/EcommerceOrders.vue'
import EcommercePlugins from '@/components/Plugins.vue'
import EcommerceArchive from '@/components/EcommerceArchive.vue'
import EcommerceWebsiteOverview from '@/components/Website.vue'
import apiIntegrationIcon from '@/assets/apps-menu/api-integration.svg'
import chevronRightIcon from '@/assets/apps-menu/chevron-right.svg'
import instagramIcon from '@/assets/apps-menu/instagram.svg'
import messengerIcon from '@/assets/apps-menu/messenger.svg'
import aakashSmsIcon from '@/assets/apps-menu/aakash-sms.png'
import aiChipIcon from '@/assets/apps-menu/ai-chip.svg'
import ecommerceIcon from '@/assets/apps-menu/ecommerce.svg'
import mcpServerIcon from '@/assets/apps-menu/mcp-server.svg'
import searchIcon from '@/assets/apps-menu/search.svg'
import sidebarToggleIcon from '@/assets/apps-menu/sidebar-toggle.svg'
import sparrowSmsIcon from '@/assets/apps-menu/sparrow-sms.png'
import verifiedBadgeIcon from '@/assets/apps-menu/verified-badge.svg'
import webhookIcon from '@/assets/apps-menu/webhook.svg'
import {
  consumeRequestedEcommerceTool,
  ECOMMERCE_TOOL_EVENT,
  notifyEcommerceFeatureChange,
} from '@/utils/ecommerceNavigation'

const route = useRoute()
const router = useRouter()
const { setOpen } = useSidebar()
const Frappe_URL = import.meta.env.VITE_FRAPPE_URL || ''
const INTEGRATION_TAB_STORAGE_KEY = 'ecommerce.activeIntegrationTab'
const isEcommerceEnabled = ref(false)
const ecommerceFeatureLoading = ref(true)
const ecommerceFeatureSaving = ref(false)
const ecommerceFeatureError = ref('')
const appsViewMode = ref('row')
const enablewebhook = ref(0)
const pages = ref([])
const selectedPageId = ref('')
const selectedInstaPageId = ref('')
const selectedPageName = ref('')
const selectedInstaPage = ref('')
const apiUrl = '/api/method/ecommerce.api.update_table_social_social_integrations'
const WEBHOOK_SECRET_STORAGE_KEY = 'integration_webhook_secret'
const metaConnectionLoading = ref(false)

const apiKey = ref(null)
const apiSecret = ref(null)
const dialog2 = ref(false)
const dialogTitle = ref('')
const dialogMessage = ref('')
const activeTab = ref('api')
const integrationSearch = ref('')
const selectedEcommerceTool = ref('')
const ecommerceTools = [
  {
    key: 'website-builder',
    label: 'Store design',
    description: 'Update your homepage, header, footer, colors, and content.',
    icon: 'storefront',
  },
  {
    key: 'orders',
    label: 'Orders',
    description: 'Pack storefront orders, then confirm them for delivery.',
    icon: 'orders',
  },
  {
    key: 'add-product',
    label: 'Products',
    description: 'Add products and update photos, prices, options, and stock.',
    icon: 'add_box',
  },
  {
    key: 'categories',
    label: 'Product categories',
    description: 'Group similar products so customers can find them easily.',
    icon: 'category',
  },
  {
    key: 'brands',
    label: 'Brands (optional)',
    description: 'Add brand names and logos only when your products need them.',
    icon: 'sell',
  },
  {
    key: 'analytics',
    label: 'Analytics',
    description: 'Review ecommerce performance and activity.',
    icon: 'analytics',
  },
  {
    key: 'plugins',
    label: 'Advanced features',
    description: 'Add optional extensions after your store is working.',
    icon: 'extension',
  },
  {
    key: 'archive',
    label: 'Archive',
    description: 'Review and restore archived ecommerce data.',
    icon: 'archive',
  },
]
const ecommerceComponentMap = {
  orders: EcommerceOrders,
  analytics: EcommerceAnalytics,
  brands: EcommerceBrands,
  categories: EcommerceCategories,
  'add-product': EcommerceAddProduct,
  plugins: EcommercePlugins,
  archive: EcommerceArchive,
}
const ecommerceMenuValue = computed({
  get: () => selectedEcommerceTool.value || 'overview',
  set: (tool) => {
    if (tool === 'overview') {
      handleEcommerceBack()
      return
    }
    if (tool === 'website-builder') {
      navigateEcommerceTool(tool)
      return
    }
    navigateEcommerceTool(tool)
  },
})
const selectedEcommerceToolMeta = computed(
  () =>
    ecommerceTools.find((tool) => tool.key === selectedEcommerceTool.value) ||
    ecommerceTools[0],
)
const selectedEcommerceComponent = computed(
  () => ecommerceComponentMap[selectedEcommerceTool.value] || null,
)
const isEcommerceCollectionTool = computed(() =>
  ['add-product', 'categories', 'brands', 'archive', 'orders'].includes(
    selectedEcommerceTool.value,
  ),
)

function openRequestedEcommerceTool(tool) {
  if (!ecommerceComponentMap[tool]) return
  navigateEcommerceTool(tool)
}

function navigateEcommerceTool(tool, { replace = false } = {}) {
  if (ecommerceFeatureLoading.value || !isEcommerceEnabled.value) {
    activeTab.value = 'ecommerce'
    selectedEcommerceTool.value = ''
    const destination = {
      name: 'apiintegration',
      params: { integrationTab: 'ecommerce' },
      query: { ...route.query },
    }
    if (replace) router.replace(destination)
    else router.push(destination)
    return
  }
  if (tool === 'website-builder') {
    router.push({ name: 'WebsiteHome' })
    return
  }
  if (!ecommerceComponentMap[tool]) return
  activeTab.value = 'ecommerce'
  selectedEcommerceTool.value = tool
  const currentTab = String(route.params.integrationTab || '')
  const currentTool = String(route.params.integrationTool || '')
  if (currentTab === 'ecommerce' && currentTool === tool) return
  const destinationQuery = { ...route.query }
  if (currentTool !== tool) delete destinationQuery.item
  const destination = {
    name: 'apiintegration',
    params: { integrationTab: 'ecommerce', integrationTool: tool },
    query: destinationQuery,
  }
  if (replace) router.replace(destination)
  else router.push(destination)
}

function handleEcommerceToolRequest(event) {
  openRequestedEcommerceTool(event.detail?.tool)
  window.sessionStorage.removeItem('ecommerce.pendingEcommerceTool')
}
const isEcommerceToolOpen = computed(
  () => activeTab.value === 'ecommerce' && Boolean(selectedEcommerceTool.value),
)
const isMobile = ref(false)
const showMenuMobile = ref(true)
const isIntegrationSidebarOpen = ref(true)
const request_url = ref(webhook.data?.url || '')
const webhookKey = ref('')
const message = ref('')
const error = ref('')
const sandboxOrderId = ref('')
const sandboxStatus = ref('')
const sandboxLoading = ref(false)
const sandboxMessage = ref('')
const sandboxError = ref('')
const sandboxResponse = ref('')
const showSandboxDemoDetails = ref(false)
const blockedAppHosts = new Set([
  'www.pickndropnepal.com',
  'pickndropnepal.com',
])
const sandboxStatusOptions = [
  {
    value: 'package_pickup_assigned',
    label: 'package_pickup_assigned',
  },
  {
    value: 'package_pickup_1st_attempt_failed',
    label: 'package_pickup_1st_attempt_failed',
  },
  {
    value: 'package_pickup_reattempt_failed',
    label: 'package_pickup_reattempt_failed',
  },
  {
    value: 'package_pickup_success',
    label: 'package_pickup_success',
  },
  {
    value: 'waiting_for_drop_off',
    label: 'waiting_for_drop_off',
  },
  {
    value: 'package_arrived_at_hub',
    label: 'package_arrived_at_hub',
  },
  {
    value: 'package_received_at_hub',
    label: 'package_received_at_hub',
  },
  {
    value: 'received_at_lastmile_station',
    label: 'received_at_lastmile_station',
  },
  {
    value: 'package_ready_to_dispatch_last_mile_station',
    label: 'package_ready_to_dispatch_last_mile_station',
  },
  {
    value: 'package_dispatched_to_last_mile_station_transporter',
    label: 'package_dispatched_to_last_mile_station_transporter',
  },
  {
    value: 'package_stationed_in_from_transporter',
    label: 'package_stationed_in_from_transporter',
  },
  {
    value: 'ready_for_dispatched_last_mile_hero',
    label: 'ready_for_dispatched_last_mile_hero',
  },
  {
    value: 'out_for_delivery',
    label: 'out_for_delivery',
  },
  {
    value: 'about_to_deliver',
    label: 'about_to_deliver',
  },
  {
    value: '1st_attempt_failed',
    label: '1st_attempt_failed',
  },
  {
    value: 'package_redelivery',
    label: 'package_redelivery',
  },
  {
    value: 'package_reattempts_failed',
    label: 'package_reattempts_failed',
  },
  {
    value: 'delivered',
    label: 'delivered',
  },
  {
    value: 'delivery_failed_and_cancelled',
    label: 'delivery_failed_and_cancelled',
  },
  {
    value: 'return_at_transit_hub',
    label: 'return_at_transit_hub',
  },
  {
    value: 'package_returned_from_transit_hub_to_transporter',
    label: 'package_returned_from_transit_hub_to_transporter',
  },
  {
    value: 'received_from_transporter_to_dispatched_hub',
    label: 'received_from_transporter_to_dispatched_hub',
  },
  {
    value: 'fd_package_ready_to_return_to_shipper',
    label: 'fd_package_ready_to_return_to_shipper',
  },
  {
    value: 'package_returned',
    label: 'package_returned',
  },
  {
    value: 'package_returned_from_lastmile_sation_to_transporter',
    label: 'package_returned_from_lastmile_sation_to_transporter',
  },
  {
    value: 'cr_package_ready_to_delivered_to_qcc',
    label: 'cr_package_ready_to_delivered_to_qcc',
  },
]
const isWebhookEnabled = ref(webhook.data?.enabled === 1)
const isFeatureEnabled = ref(true)
const selectedOptions = ref(['Completed'])
const statusWebhookName = ref(webhook.data?.webhook_name || '')
const statusToggleReady = ref(false)
const mcpEndpoint = 'https://mcp.pickndropnepal.com/mcp'
const mcpClientTab = ref('claude')
const mcpEndpointCopied = ref(false)
const mcpConfigCopied = ref(false)
const mcpActiveStep = ref(0)
const mcpFlowPlaying = ref(true)
let handleResize = null
let mcpFlowTimer = null

const isDesktopCollapsed = computed(
  () => !isMobile.value && !isIntegrationSidebarOpen.value,
)
const desktopIntegrationGridStyle = computed(() => {
  if (isMobile.value) {
    return {}
  }

  return {
    gridTemplateColumns: isDesktopCollapsed.value
      ? `${SIDEBAR_WIDTH_ICON} minmax(0, 1fr)`
      : `${activeTab.value === 'ecommerce' ? '13rem' : SIDEBAR_WIDTH} minmax(0, 1fr)`,
  }
})

const integrationTabs = [
  {
    key: 'api',
    label: 'API Integration',
    menuBadge: 'Free',
    verified: true,
    menuIcon: apiIntegrationIcon,
    iconFillsTile: true,
    iconClass: '',
    tileClass: '',
    tileStyle: undefined,
    cornerBadge: '',
    cornerBadgeClass: '',
    title: 'API Integration',
    subtitle: 'Demo access, keys, and production setup',
    eyebrow: 'API Access',
    heading: 'Connect your system to Pick & Drop',
    description:
      'Use the demo environment first, then generate production credentials when your integration is ready.',
  },
  {
    key: 'webhook',
    label: 'Webhook',
    menuBadge: 'Free',

    verified: true,
    menuIcon: webhookIcon,
    iconFillsTile: true,
    iconClass: '',
    tileClass: '',
    tileStyle: undefined,
    cornerBadge: '',
    cornerBadgeClass: '',
    title: 'Webhook Integration',
    subtitle: 'Realtime package updates',
    eyebrow: 'Event Delivery',
    heading: 'Push shipment events to your endpoint',
    description:
      'Receive package status updates and comments automatically in your external system.',
  },
  {
    key: 'messenger',
    label: 'Messenger',
    groupLabel: 'Social & Messaging',
    menuBadge: 'Free',
    menuSubtitle: 'Meta',
    verified: true,
    menuIcon: messengerIcon,
    iconFillsTile: true,
    iconClass: '',
    tileClass: '',
    tileStyle: undefined,
    cornerBadge: '',
    cornerBadgeClass: '',
    title: 'Messenger Integration',
    subtitle: 'Facebook page messaging connection',
    eyebrow: 'Social Messaging',
    heading: 'Connect Facebook Messenger',
    description:
      'Authorize your Facebook account, choose the page, and manage customer conversations from the connected flow.',
  },
  {
    key: 'instagram',
    label: 'Instagram',
    menuBadge: 'Free',
    menuSubtitle: 'Meta',
    verified: true,
    menuIcon: instagramIcon,
    iconFillsTile: true,
    iconClass: '',
    tileClass: '',
    tileStyle: undefined,
    cornerBadge: '',
    cornerBadgeClass: '',
    title: 'Instagram Integration',
    subtitle: 'Professional account connection',
    eyebrow: 'Social Messaging',
    heading: 'Connect Instagram messaging',
    description:
      'Connect an Instagram professional account linked to Facebook for support and automation use cases.',
  },
  {
    key: 'sparrow-sms',
    label: 'Sparrow SMS',
    groupLabel: 'SMS Gateway',
    menuBadge: 'Free',
    menuSubtitle: 'Sparrow SMS Pvt. Ltd.',
    verified: true,
    menuIcon: sparrowSmsIcon,
    iconClass: '',
    tileClass: 'border border-[#f0f0f0] bg-white',
    tileStyle: undefined,
    cornerBadge: 'NEW',
    cornerBadgeClass: 'bg-[#dc2626]',
    title: 'Sparrow SMS',
    subtitle: 'Transactional SMS provider',
    eyebrow: 'SMS Gateway',
    heading: 'Connect Sparrow SMS',
    description:
      'Set up transactional messaging for alerts, OTP, and delivery-related notifications.',
  },
  {
    key: 'aakash-sms',
    label: 'Aakash SMS',
    menuBadge: 'Free',
    menuSubtitle: 'Aakash SMS Pvt. Ltd.',
    verified: true,
    menuIcon: aakashSmsIcon,
    iconClass: '',
    tileClass: 'bg-[#374151]',
    tileStyle: undefined,
    cornerBadge: 'NEW',
    cornerBadgeClass: 'bg-[#dc2626]',
    title: 'Aakash SMS',
    subtitle: 'Transactional SMS provider',
    eyebrow: 'SMS Gateway',
    heading: 'Connect Aakash SMS',
    description:
      'Integrate Aakash SMS for customer communication and shipment message delivery.',
  },
  {
    key: 'mcp-server',
    label: 'MCP Server',
    groupLabel: 'AI',
    menuBadge: 'Free',
    menuSubtitle: 'AI Tools & Orchestration',
    verified: true,
    menuIcon: mcpServerIcon,
    iconFillsTile: true,
    iconClass: '',
    tileClass: '',
    tileStyle: undefined,
    cornerBadge: 'NEW',
    cornerBadgeClass: 'bg-[#dc2626]',
    title: 'MCP Server',
    subtitle: 'AI workflow integration',
    eyebrow: 'AI',
    eyebrowIcon: aiChipIcon,
    heading: 'Connect MCP Server',
    description:
      'Bring AI-powered tools and orchestration workflows into the Pick & Drop apps environment.',
  },

  {
    key: 'ecommerce',
    label: 'ECommerce',
    groupLabel: 'ECommerce',
    menuBadge: 'Free',
    menuSubtitle: 'Pick & Drop',
    verified: true,
    menuIcon: ecommerceIcon,
    iconFillsTile: true,
    iconClass: '',
    tileClass: '',
    tileStyle: undefined,
    cornerBadge: 'BETA',
    cornerBadgeClass: 'bg-[#16a34a]',
    title: 'ECommerce',
    subtitle: 'Store tools and commerce management',
    eyebrow: 'ECommerce',
    heading: 'Manage ECommerce',
    description:
      'Manage products, brands, categories, analytics, plugins, and your storefront from one place.',
  },


]

const hiddenIntegrationTabKeys = new Set([
  'sparrow-sms',
  'aakash-sms',
  'ecommerce',
  'messenger',
  'instagram',
])

const visibleIntegrationTabs = computed(() =>
  integrationTabs
    .filter((tab) => !hiddenIntegrationTabKeys.has(tab.key))
    .map((tab) => {
      if (tab.key !== 'ecommerce' || isEcommerceEnabled.value) return tab
      return {
        ...tab,
        verified: false,
        menuBadge: ecommerceFeatureLoading.value ? '' : 'Enable',
        tileClass: 'border border-gray-200 bg-gray-100 grayscale opacity-70',
        subtitle: 'Disabled until you enable it',
        heading: 'Enable ECommerce',
        description:
          'Turn on ECommerce to create a storefront, manage products, and process online orders.',
      }
    }),
)

function ecommerceRequestHeaders() {
  const token = localStorage.getItem('access_token') || ''
  const headers = { 'Content-Type': 'application/json' }
  if (token) headers.Authorization = `Bearer ${token}`
  if (window.frappe?.csrf_token) {
    headers['X-Frappe-CSRF-Token'] = window.frappe.csrf_token
  }
  return headers
}

function unwrapFrappeResponse(payload) {
  return payload?.message ?? payload
}

async function loadEcommerceFeatureStatus() {
  ecommerceFeatureLoading.value = true
  ecommerceFeatureError.value = ''
  try {
    const response = await fetch(
      `${Frappe_URL}/api/method/ecommerce.api.get_ecommerce_feature_status`,
      { headers: ecommerceRequestHeaders() },
    )
    const payload = await response.json().catch(() => ({}))
    const result = unwrapFrappeResponse(payload)
    if (!response.ok || result?.status !== 'success') {
      throw new Error(result?.message || 'Unable to load ECommerce status.')
    }
    isEcommerceEnabled.value = Boolean(result?.data?.enabled)
  } catch (requestError) {
    isEcommerceEnabled.value = false
    ecommerceFeatureError.value =
      requestError?.message || 'Unable to load ECommerce status.'
  } finally {
    ecommerceFeatureLoading.value = false
  }
}

async function updateEcommerceFeature(enabled) {
  if (ecommerceFeatureSaving.value) return
  ecommerceFeatureSaving.value = true
  ecommerceFeatureError.value = ''
  try {
    const response = await fetch(
      `${Frappe_URL}/api/method/ecommerce.api.set_ecommerce_feature_status`,
      {
        method: 'POST',
        headers: ecommerceRequestHeaders(),
        body: JSON.stringify({ enabled }),
      },
    )
    const payload = await response.json().catch(() => ({}))
    const result = unwrapFrappeResponse(payload)
    if (!response.ok || result?.status !== 'success') {
      throw new Error(result?.message || 'Unable to update ECommerce status.')
    }
    isEcommerceEnabled.value = Boolean(result?.data?.enabled)
    notifyEcommerceFeatureChange(isEcommerceEnabled.value)
    if (!isEcommerceEnabled.value) selectedEcommerceTool.value = ''
  } catch (requestError) {
    ecommerceFeatureError.value =
      requestError?.message || 'Unable to update ECommerce status.'
  } finally {
    ecommerceFeatureSaving.value = false
  }
}

watch(
  [
    () => route.params.integrationTab,
    () => route.params.integrationTool,
    () => route.query.integration,
  ],
  ([routeTab, routeTool, queryTab]) => {
    const parameterTab = Array.isArray(routeTab) ? routeTab[0] : routeTab
    const parameterTool = Array.isArray(routeTool) ? routeTool[0] : routeTool
    const tabKey = Array.isArray(queryTab) ? queryTab[0] : queryTab
    const storedTab = localStorage.getItem(INTEGRATION_TAB_STORAGE_KEY)
    const requestedTab = parameterTab || tabKey || storedTab
    const isValidTab = visibleIntegrationTabs.value.some(
      (tab) => tab.key === requestedTab,
    )

    activeTab.value = isValidTab ? requestedTab : 'api'
    localStorage.setItem(INTEGRATION_TAB_STORAGE_KEY, activeTab.value)
    if (activeTab.value !== 'ecommerce') {
      selectedEcommerceTool.value = ''
    } else {
      const pendingTool = consumeRequestedEcommerceTool()
      const requestedTool = ecommerceComponentMap[parameterTool]
        ? parameterTool
        : pendingTool
      selectedEcommerceTool.value = ecommerceComponentMap[requestedTool]
        ? requestedTool
        : ''
      if (!parameterTool && selectedEcommerceTool.value) {
        navigateEcommerceTool(selectedEcommerceTool.value, { replace: true })
      }
    }
  },
  { immediate: true },
)

const filteredIntegrationTabs = computed(() => {
  const term = integrationSearch.value.trim().toLowerCase()
  if (!term) return visibleIntegrationTabs.value

  return visibleIntegrationTabs.value.filter((tab) =>
    [tab.label, tab.title, tab.subtitle, tab.description].some((value) =>
      value.toLowerCase().includes(term),
    ),
  )
})

const activeTabMeta = computed(
  () =>
    visibleIntegrationTabs.value.find((tab) => tab.key === activeTab.value) ||
    visibleIntegrationTabs.value[0],
)

function isTabVisuallyActive(tab) {
  return (
    activeTab.value === tab.key &&
    (tab.key !== 'ecommerce' || isEcommerceEnabled.value)
  )
}

const mcpClientTabs = [
  { key: 'claude', label: 'Claude Desktop' },
  { key: 'cursor', label: 'Cursor' },
  { key: 'vscode', label: 'VS Code' },
  { key: 'other', label: 'Other clients' },
]

const mcpConfigMap = {
  claude: {
    label: 'claude_desktop_config.json',
    value: `{
  "mcpServers": {
    "pickndrop": {
      "url": "${mcpEndpoint}"
    }
  }
}`,
  },
  cursor: {
    label: '~/.cursor/mcp.json',
    value: `{
  "mcpServers": {
    "pickndrop": {
      "url": "${mcpEndpoint}"
    }
  }
}`,
  },
  vscode: {
    label: '.vscode/mcp.json',
    value: `{
  "servers": {
    "pickndrop": {
      "type": "http",
      "url": "${mcpEndpoint}"
    }
  }
}`,
  },
  other: {
    label: 'mcp.json',
    value: `{
  "mcpServers": {
    "pickndrop": {
      "url": "${mcpEndpoint}"
    }
  }
}`,
  },
}

const mcpFeatures = [
  'Model Context Protocol compatible',
  'OAuth authentication',
  'Order management',
  'Shipment tracking',
  'Vendor management',
  'Branch lookup',
  'Delivery charge calculation',
  'Analytics',
  'Payment information',
  'Webhook management',
  'Sandbox test mode',
]

const mcpTools = [
  'Company',
  'Branches',
  'Orders',
  'Order Comments',
  'Vendors',
  'Payments',
  'Delivery Charges',
  'Analytics',
  'Webhooks',
]

const mcpSupportedClients = [
  'Claude Desktop',
  'ChatGPT',
  'Cursor',
  'VS Code',
  'Windsurf',
  'Cline',
  'Continue',
  'Custom MCP clients',
]

const mcpFlowSteps = [
  { label: 'Configure your MCP client.' },
  { label: 'Connect to the MCP endpoint.' },
  { label: 'Authenticate with OAuth.' },
  { label: 'Discover the available tools.' },
  { label: 'Invoke the required tools.' },
  { label: 'Receive structured JSON responses.' },
]

const activeMcpConfig = computed(
  () => mcpConfigMap[mcpClientTab.value]?.value || mcpConfigMap.claude.value,
)

const activeMcpConfigLabel = computed(
  () => mcpConfigMap[mcpClientTab.value]?.label || mcpConfigMap.claude.label,
)

function setTemporaryFlag(flagRef) {
  flagRef.value = true
  window.clearTimeout(flagRef._timer)
  flagRef._timer = window.setTimeout(() => {
    flagRef.value = false
  }, 1600)
}

async function copyToClipboard(text) {
  try {
    await navigator.clipboard.writeText(text)
  } catch {
    const textarea = document.createElement('textarea')
    textarea.value = text
    document.body.appendChild(textarea)
    textarea.select()
    document.execCommand('copy')
    textarea.remove()
  }
}

async function copyMcpEndpoint() {
  await copyToClipboard(mcpEndpoint)
  setTemporaryFlag(mcpEndpointCopied)
}

async function copyMcpConfig() {
  await copyToClipboard(activeMcpConfig.value)
  setTemporaryFlag(mcpConfigCopied)
}

function stopMcpFlowTimer() {
  if (mcpFlowTimer) {
    window.clearTimeout(mcpFlowTimer)
    mcpFlowTimer = null
  }
}

function startMcpFlowTimer() {
  stopMcpFlowTimer()
  mcpFlowTimer = window.setTimeout(() => {
    if (mcpFlowPlaying.value) {
      mcpActiveStep.value = (mcpActiveStep.value + 1) % mcpFlowSteps.length
      startMcpFlowTimer()
    }
  }, 1500)
}

function toggleMcpFlowPlayback() {
  mcpFlowPlaying.value = !mcpFlowPlaying.value
}

function setMcpFlowStep(index) {
  mcpActiveStep.value = index
  mcpFlowPlaying.value = false
}

const activePlatform = computed(() =>
  activeTab.value === 'instagram' ? 'Instagram' : 'Facebook',
)

const filteredPages = computed(() =>
  pages.value.filter((pageItem) => pageItem.social === activePlatform.value),
)

const selectedPlatformPageId = computed({
  get() {
    return activeTab.value === 'instagram'
      ? selectedInstaPageId.value
      : selectedPageId.value
  },
  set(value) {
    if (activeTab.value === 'instagram') {
      selectedInstaPageId.value = value
    } else {
      selectedPageId.value = value
    }
  },
})

const selectedPlatformPageName = computed(() =>
  activeTab.value === 'instagram'
    ? selectedInstaPage.value
    : selectedPageName.value,
)

const selectTab = (key) => {
  activeTab.value = key
  localStorage.setItem(INTEGRATION_TAB_STORAGE_KEY, key)
  if (key === 'ecommerce') {
    selectedEcommerceTool.value = ''
  }
  const { integration, item, ...remainingQuery } = route.query
  router.replace({
    name: 'apiintegration',
    params: { integrationTab: key },
    query: remainingQuery,
  })
  if (isMobile.value) {
    showMenuMobile.value = false
  }
}

const handleEcommerceBack = () => {
  selectedEcommerceTool.value = ''
  const destinationQuery = { ...route.query }
  delete destinationQuery.item
  router.push({
    name: 'apiintegration',
    params: { integrationTab: 'ecommerce' },
    query: destinationQuery,
  })
}

const handleIntegrationKeydown = (event) => {
  if (
    event.key === 'Escape' &&
    isEcommerceToolOpen.value &&
    !document.querySelector('[role="dialog"]')
  ) {
    event.preventDefault()
    handleEcommerceBack()
  }
}

watch(
  [isMobile, isIntegrationSidebarOpen],
  ([mobile, isOpen]) => {
    if (!mobile) {
      setOpen(!isOpen)
    }
  },
  { immediate: true },
)

watch(
  () => webhook.data,
  (val) => {
    statusToggleReady.value = false
    if (val) {
      statusWebhookName.value = val.webhook_name || ''
      request_url.value = val.url || request_url.value
      isWebhookEnabled.value = val.enabled === 1
      enablewebhook.value = val.enabled ?? 0
    }
    statusToggleReady.value = true
  },
  { immediate: true },
)

const fetchWebhookData = async () => {
  try {
    const webhookData = await webhook.fetch()
    if (webhookData && webhookData.enabled !== undefined) {
      enablewebhook.value = webhookData.enabled
    }
  } catch (error) {
    console.error('Error fetching webhook data:', error)
  }
}

const toggleWebhookState = async (name, enabled) => {
  if (!name) {
    dialogTitle.value = 'Webhook Not Found'
    dialogMessage.value = 'Please configure the webhook URL first.'
    dialog2.value = true
    return
  }

  try {
    const response = await fetch('/api/method/ecommerce.webhook.toggle_webhook', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ webhook_name: name, enabled }),
    })

    let data = {}
    try {
      data = await response.json()
    } catch (parseError) {
      data = {}
    }

    if (!response.ok || (data.status && data.status !== 'success')) {
      throw new Error(data.message || 'Unable to update webhook state.')
    }

    enablewebhook.value = enabled ? 1 : 0
  } catch (toggleError) {
    isWebhookEnabled.value = !enabled
    dialogTitle.value = 'Webhook Update Failed'
    dialogMessage.value =
      toggleError.message || 'Failed to update webhook state.'
    dialog2.value = true
  }
}

const handleStatusToggle = async (value) => {
  if (!statusToggleReady.value) return
  await toggleWebhookState(statusWebhookName.value, value)
}

const isBlockedAppHost = () => {
  if (typeof window === 'undefined') return false
  return blockedAppHosts.has(window.location.hostname.toLowerCase())
}

const handleConnect = async () => {
  message.value = ''
  error.value = ''

  if (!request_url.value || !webhookKey.value) {
    error.value = 'Both Base URL and Webhook Key are required!'
    return
  }

 //  //console.log("request_url.value", request_url.value)

  try {
    const response = await fetch('/api/method/ecommerce.webhook.get_status', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        request_url: request_url.value,
        webhook_secret: webhookKey.value,
        webhook_mode: selectedOptions.value,
        enabled: isWebhookEnabled.value,
      }),
    })

    if (!response.ok) {
      throw new Error('Failed to connect. Please try again.')
    }

    await response.json()
    localStorage.setItem(WEBHOOK_SECRET_STORAGE_KEY, webhookKey.value)
    message.value = 'Webhook added successfully'
    await fetchWebhookData()
  } catch (connectError) {
    error.value = connectError.message || 'An error occurred.'
  }
}

const sendWebhookSandbox = async () => {
  sandboxMessage.value = ''
  sandboxError.value = ''
  sandboxResponse.value = ''
  showSandboxDemoDetails.value = false

  if (!request_url.value) {
    sandboxError.value = 'Base URL is required before testing.'
    return
  }

  if (isBlockedAppHost()) {
    sandboxError.value =
      'Sandbox requests are not allowed on the production server.'
    showSandboxDemoDetails.value = true
    return
  }

  if (!sandboxOrderId.value || !sandboxStatus.value) {
    sandboxError.value = 'Order ID and status are required.'
    return
  }

  sandboxLoading.value = true

  try {
    const response = await fetch(
      '/api/method/ecommerce.api.receive_ldm_webhook',
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          request_url: request_url.value,
          orderID: sandboxOrderId.value,
          status: sandboxStatus.value,
        }),
      },
    )

    const data = await response.json()
    const result = data.message || data


    if (!response.ok || result.status !== 'success') {
      throw new Error(
        result.message || 'Failed to send sandbox webhook request.',
      )
    }

    sandboxMessage.value = `Sandbox request sent successfully${result.http_status ? ` (HTTP ${result.http_status})` : ''}.`
    sandboxResponse.value = JSON.stringify(result, null, 2)
  } catch (sandboxRequestError) {
    console.error('Sandbox webhook error:', sandboxRequestError)
    sandboxError.value =
      sandboxRequestError.message || 'Failed to send sandbox webhook request.'
  } finally {
    sandboxLoading.value = false
  }
}

const fetchPageDetails = async () => {
  try {
    const data = await page.fetch()
    if (data.message && data.data && data.data.length > 0) {
      pages.value = data.data.map((item) => ({
        social: item.social_media,
        id: item.page_id,
        name: item.page_name,
        status_code: item.status_code,
      }))

      const defaultFacebookPage = pages.value.find(
        (pageItem) =>
          pageItem.status_code === 1 && pageItem.social === 'Facebook',
      )
      const defaultInstagramPage = pages.value.find(
        (pageItem) =>
          pageItem.status_code === 1 && pageItem.social === 'Instagram',
      )

      selectedPageName.value = defaultFacebookPage
        ? defaultFacebookPage.name
        : ''
      selectedPageId.value = defaultFacebookPage
        ? defaultFacebookPage.id
        : ''
      selectedInstaPage.value = defaultInstagramPage
        ? defaultInstagramPage.name
        : ''
      selectedInstaPageId.value = defaultInstagramPage
        ? defaultInstagramPage.id
        : ''
    }
  } catch (error) {
    console.error('Error fetching page details:', error)
  }
}

const sendPageIdToBackend = async (pageId, platform) => {
  if (!pageId || !platform) return

  try {
    const response = await fetch(apiUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ page_id: pageId, platform }),
    })

    const payload = await response.json()
    const result = payload.message || payload
    if (!response.ok || result.status !== 'success') {
      throw new Error(result.message || `Could not connect ${platform}.`)
    }

    const selectedPage = pages.value.find(
      (pageItem) =>
        pageItem.id === pageId && pageItem.social === platform,
    )
    if (platform === 'Instagram') {
      selectedInstaPage.value = selectedPage?.name || ''
    } else {
      selectedPageName.value = selectedPage?.name || ''
    }
    pages.value = pages.value.map((pageItem) => ({
      ...pageItem,
      status_code:
        pageItem.social === platform
          ? Number(pageItem.id === pageId)
          : pageItem.status_code,
    }))
  } catch (error) {
    console.error('Error sending page ID to backend:', error)
    dialogTitle.value = `${platform} Connection Failed`
    dialogMessage.value =
      error.message || `Could not connect the selected ${platform} account.`
    dialog2.value = true
    await fetchPageDetails()
  }
}

const handlePageSelection = (platform) => {
  const pageId =
    platform === 'Instagram' ? selectedInstaPageId.value : selectedPageId.value
  if (pageId) {
    sendPageIdToBackend(pageId, platform)
  }
}

const getFrappeErrorMessage = (payload, fallback) => {
  if (typeof payload?.message === 'string' && payload.message) {
    return payload.message
  }
  try {
    const serverMessages = JSON.parse(payload?._server_messages || '[]')
    for (const rawMessage of serverMessages) {
      const parsed = typeof rawMessage === 'string' ? JSON.parse(rawMessage) : rawMessage
      if (parsed?.message) {
        const wrapper = document.createElement('div')
        wrapper.innerHTML = parsed.message
        return wrapper.textContent || fallback
      }
    }
  } catch (_error) {
    // Use the safe fallback when Frappe did not return structured messages.
  }
  return fallback
}

const connectToMeta = async (platform) => {
  if (metaConnectionLoading.value) return
  metaConnectionLoading.value = true
  try {
    const token = localStorage.getItem('access_token')
    const response = await fetch(
      `${Frappe_URL}/api/method/ecommerce.meta_oauth.get_authorization_url`,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
        },
        body: JSON.stringify({ platform }),
      },
    )
    const payload = await response.json()
    const result = payload.message || payload
    if (!response.ok || !result.authorization_url) {
      throw new Error(
        getFrappeErrorMessage(payload, `Could not start ${platform} login.`),
      )
    }
    window.location.assign(result.authorization_url)
  } catch (error) {
    metaConnectionLoading.value = false
    dialogTitle.value = `${platform} Connection Failed`
    dialogMessage.value =
      error.message || `Could not start the ${platform} connection.`
    dialog2.value = true
  }
}

const connectToMessenger = () => connectToMeta('Facebook')
const connectToInstagram = () => connectToMeta('Instagram')

const handleMetaConnectionResult = () => {
  const status = String(route.query.meta_connection || '')
  if (!status) return
  const message = String(route.query.meta_message || '')
  dialogTitle.value =
    status === 'success' ? 'Meta Connection Complete' : 'Meta Connection Failed'
  dialogMessage.value =
    message ||
    (status === 'success'
      ? 'Your Meta account was connected successfully.'
      : 'Meta could not complete the connection.')
  dialog2.value = true
  const { meta_connection, meta_message, ...remainingQuery } = route.query
  router.replace({ query: remainingQuery })
}

const generateApiKeys = async () => {
  const token = localStorage.getItem('access_token')
  try {
    const response = await fetch(
      `${Frappe_URL}/api/method/ecommerce.get_role_profile_of_logged_user.generate_keys`,
      {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${token}`,
        },
      },
    )

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    const data = await response.json()

    if (data.message.message === 'Demo user cannot generate API key') {
      dialogTitle.value = 'Error'
      dialogMessage.value = 'Demo user cannot generate API key.'
      dialog2.value = true
      return
    }

    if (data.message.api_secret) {
      apiKey.value = data.message.api_key
      apiSecret.value = data.message.api_secret
      dialogTitle.value = 'API Secret'
      dialogMessage.value = `Save API Secret: ${apiSecret.value}, Api Key: ${data.message.api_key}`
      dialog2.value = true
    }
  } catch (error) {
    if (error.message.includes('PermissionError')) {
      dialogTitle.value = 'Permission Error'
      dialogMessage.value = 'You do not have permission to generate API keys.'
    } else {
      dialogTitle.value = 'Error'
      dialogMessage.value = 'An error occurred while generating API keys.'
    }
    dialog2.value = true
  }
}

const goToApiDetails = () => {
  router.push('/integration')
}

onMounted(() => {
  handleResize = () => {
    isMobile.value = window.innerWidth < 768
    if (!isMobile.value) {
      showMenuMobile.value = true
    }
  }

  handleResize()
  window.addEventListener('resize', handleResize)
  window.addEventListener('keydown', handleIntegrationKeydown)
  window.addEventListener(ECOMMERCE_TOOL_EVENT, handleEcommerceToolRequest)
  loadEcommerceFeatureStatus()
  fetchWebhookData()
  handleMetaConnectionResult()
  fetchPageDetails()
})

onBeforeUnmount(() => {
  if (handleResize) {
    window.removeEventListener('resize', handleResize)
  }
  window.removeEventListener('keydown', handleIntegrationKeydown)
  window.removeEventListener(ECOMMERCE_TOOL_EVENT, handleEcommerceToolRequest)
  setOpen(true)
})
</script>

<style scoped>
@keyframes ecommerce-content-in {
  from {
    opacity: 0;
    transform: translateY(4px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.ecommerce-content-panel {
  animation: ecommerce-content-in 160ms ease-out;
}

@media (prefers-reduced-motion: reduce) {
  .ecommerce-content-panel {
    animation: none;
  }
}
</style>
