<script setup lang="ts">
import {onBeforeMount, ref} from "vue";
import {
  ChevronDownIcon,
  ChevronLeftIcon,
  ChevronRightIcon,
  ChevronDoubleLeftIcon,
  ChevronDoubleRightIcon
} from "@heroicons/vue/20/solid";
import {MagnifyingGlassIcon} from "@heroicons/vue/24/outline";

const api_base_url = "http://localhost:5000/api";

const tabs = ref<{ name: string; href: string; current: boolean }[]>([]);

const current_log_file = ref<string[]>([]);
const page_number = ref(1);
const is_search_active = ref(false);
const selected_log_index = ref(-1);
const selected_log_name = ref("");
const page_total = ref(0);
const logs_loading = ref(false);
const page_size = 100; // Number of lines per page

// search specific variables
const searchQuery = ref("");
const occurrences = ref<number[]>([]);
let current_occurrence_index = -1;


// Function to perform search within the current log file
function performSearch() {
  if (searchQuery.value.trim() === "") {
    // If the search query is empty, refetch the current page to reset the view
    fetchLogPage();
    return;
  }
  logs_loading.value = true;
  let url = api_base_url + `/logs/search?file_name=${selected_log_name.value}&&query_str=${encodeURIComponent(searchQuery.value)}`;
  fetch(url)
      .then(response => response.json())
      .then(data => {
        current_log_file.value = data.first_match_page.lines;
        page_number.value = data.first_match_page_number;
        occurrences.value = data.occurrences;
      })
      .catch(error => {
        console.error("Error performing search:", error);
        current_log_file.value = [`${searchQuery.value} not found in the log.`];
      })
      .finally(() => {
        logs_loading.value = false;

        // Scroll to the first occurrence if found
        // timeout to ensure DOM is updated
        setTimeout(() => {
          if (!occurrences) return;
          current_occurrence_index = 0;
          jump_to_next_occurrence();
        }, 100);
      });

  is_search_active.value = true; // Hide pagination during search
}

function jump_to_next_occurrence() {
  let line_number = occurrences.value[current_occurrence_index];

  const element = document.getElementById(`line-${line_number % page_size}`);
  if (element) {
    element.scrollIntoView({behavior: 'smooth', block: 'center'});
  }
}

function handle_next_occurrence() {
  if (occurrences.value.length === 0) return;

  current_occurrence_index++;
  if (current_occurrence_index >= occurrences.value.length) {
    let url = api_base_url + `/logs/search_next?file_name=${selected_log_name.value}&&query_str=${encodeURIComponent(searchQuery.value)}&&page_number=${page_number.value + 1}`;
    logs_loading.value = true;
    fetch(url)
        .then(response => response.json())
        .then(data => {
            current_log_file.value = data.first_match_page.lines;
            page_number.value = data.first_match_page_number;
            occurrences.value = data.occurrences;
            current_occurrence_index = 0;

            // Scroll to the first occurrence on the new page
            setTimeout(() => {
              jump_to_next_occurrence();
            }, 100);
        })
        .catch(error => {
          console.error("Error fetching next search page:", error);
          current_log_file.value = ["Error fetching next search page."];
        })
        .finally(() => {
          logs_loading.value = false;

          // Scroll to the first occurrence if found
          // timeout to ensure DOM is updated
          setTimeout(() => {
            if (!occurrences) return;
            current_occurrence_index = 0;
            jump_to_next_occurrence();
          }, 100);
        });
  }

  jump_to_next_occurrence()
}

function reset_search() {
  searchQuery.value = "";
  occurrences.value = [];
  current_occurrence_index = -1;
  is_search_active.value = false;
  fetchLogPage();
}


function fetchLogPage() {
  // fetch the content of the selected log file from the backend
  let url = api_base_url + `/logs?file_name=${selected_log_name.value}&&page_number=${page_number.value}`;
  logs_loading.value = true;
  fetch(url)
      .then(response => response.json())
      .then(data => {
        current_log_file.value = data.lines;
        page_total.value = data.total_pages;
      })
      .catch(error => {
        console.error("Error fetching log content:", error);
        current_log_file.value = ["Error fetching log content."];
      })
      .finally(() => {
        logs_loading.value = false;
      });
  is_search_active.value = false;
}

function setActiveTab(index: number) {
  selected_log_index.value = index;
  selected_log_name.value = tabs.value[index].name;

  // Reset search state
  reset_search();

  fetchLogPage();
}

function highlight(line: string) {
  if (!searchQuery.value) return line;
  const regex = new RegExp(`(${searchQuery.value})`, 'gi');
  return line.replace(regex, '<mark class="bg-yellow-200 text-black">$1</mark>')
}

onBeforeMount(() => {
  // fetch the list of logs from the backend
  let url = api_base_url + "/logs/list_files"
  fetch(url)
      .then(response => response.json())
      .then(data => {
        tabs.value = data.available_logs.map((log: string) => ({
          name: log,
        }));
      })
      .catch(error => {
        console.error("Error fetching logs:", error);
      });
})
</script>

<template>

  <!-- Logo at the top -->
  <div class="flex justify-center mb-4">
    <img src="/source_logo.webp" alt="Source Logo" class="h-8 lg:h-16 w-auto"/>
  </div>

  <!-- Tabs to select log files -->
  <div v-if="tabs.length > 0" class="bg-white px-4 py-6 sm:px-6 lg:px-8 dark:bg-gray-900">
    <div class="mx-auto max-w-7xl">
      <div class="grid grid-cols-1 sm:hidden">
        <select aria-label="Select a tab" v-model="selected_log_index" @change="setActiveTab(selected_log_index)"
                class="col-start-1 row-start-1 w-full appearance-none rounded-sm bg-white py-2 pr-8 pl-3 text-base
                text-gray-900 outline-1 -outline-offset-1 outline-gray-300 focus:outline-2 focus:-outline-offset-2 focus:outline-indigo-600
                dark:bg-white/5 dark:text-gray-100 dark:outline-white/10 dark:*:bg-gray-800 dark:focus:outline-indigo-500">
          <option disabled value="-1">Select a log file</option>
          <option v-for="(tab, index) in tabs" :key="tab.name" :selected="index === selected_log_index" :value="index">
            {{
              tab.name
            }}
          </option>
        </select>
        <ChevronDownIcon
            class="pointer-events-none col-start-1 row-start-1 mr-2 size-5 self-center justify-self-end fill-gray-500 dark:fill-gray-400"
            aria-hidden="true"/>
      </div>
      <div class="hidden sm:block">
        <nav class="flex border-b border-gray-200 py-4 dark:border-white/10">
          <ul role="list"
              class="flex min-w-full flex-none gap-x-8 px-2 text-sm/6 font-semibold text-gray-500 dark:text-gray-400">
            <li v-for="(tab, index) in tabs" :key="tab.name">
              <button
                  class="cursor-pointer"
                  :class="selected_log_index === index ? 'text-indigo-600 dark:text-indigo-400' : 'hover:text-gray-700 dark:hover:text-white'"
                  @click="setActiveTab(index)">{{
                  tab.name
                }}
              </button>
            </li>
          </ul>
        </nav>
      </div>
    </div>
  </div>

  <div v-else class="flex justify-center items-center h-32">
    <p class="text-gray-500 dark:text-gray-400">No log files available.</p>
  </div>

  <!-- Log content area -->
  <div class="mt-6 px-4 sm:px-6 lg:px-8">
    <div class="mx-auto max-w-7xl">
      <div class="overflow-hidden rounded-sm border border-gray-200 dark:border-white/10">
        <div class="bg-gray-50 px-4 py-5 sm:px-6 dark:bg-gray-800">
          <h3 class="text-lg font-medium leading-6 text-gray-900 dark:text-gray-100">Build Log
            <span class="underline">{{ selected_log_name }}</span>
          </h3>
          <div v-if="current_log_file.length > 0"
               class="my-4 flex flex-col sm:flex-row sm:justify-between items-center space-y-2">
            <!-- Page controls -->
            <div v-if="!logs_loading" class="flex space-x-2">
              <!-- First page -->
              <button
                  class="flex items-center rounded-sm px-2 py-2 text-sm font-medium text-white hover:underline cursor-pointer
             disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:no-underline"
                  @click="page_number = 1; fetchLogPage()"
                  :disabled="page_number <= 1">
                <ChevronDoubleLeftIcon class="h-5 w-5"/>
                <span class="hidden sm:inline ml-1">First</span>
              </button>

              <!-- Previous -->
              <button
                  class="flex items-center rounded-sm px-2 py-2 text-sm font-medium text-white hover:underline cursor-pointer
             disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:no-underline"
                  @click="page_number--; fetchLogPage()" :disabled="page_number <= 1">
                <ChevronLeftIcon class="h-5 w-5"/>
                Previous
              </button>

              <!-- Page info -->
              <span class="self-center text-xs sm:text-sm text-gray-700 dark:text-gray-300">
      Page {{ page_number }} / {{ page_total }}
    </span>

              <!-- Next -->
              <button
                  class="flex items-center rounded-sm px-2 py-2 text-sm font-medium text-white hover:underline cursor-pointer
             disabled:opacity-50 disabled:hover:no-underline disabled:cursor-not-allowed"
                  @click="page_number++; fetchLogPage()" :disabled="page_number >= page_total">
                Next
                <ChevronRightIcon class="h-5 w-5"/>
              </button>

              <!-- Last -->
              <button
                  class="flex items-center rounded-sm px-2 py-2 text-sm font-medium text-white hover:underline cursor-pointer
             disabled:opacity-50 disabled:hover:no-underline disabled:cursor-not-allowed"
                  @click="page_number = page_total; fetchLogPage()" :disabled="page_number >= page_total">
                <span class="hidden sm:inline mr-1">Last</span>
                <ChevronDoubleRightIcon class="h-5 w-5"/>
              </button>
            </div>

            <!-- Spacer when search is active -->
            <div v-else/>

            <!-- Search bar -->
            <div class="flex items-center">
              <input
                  type="text"
                  v-model="searchQuery"
                  placeholder="Search log..."
                  @keyup.enter="performSearch()"
                  class="rounded-sm border border-gray-300 px-3 py-2 text-sm text-gray-900 focus:outline-none focus:ring-2 focus:ring-indigo-500 dark:bg-gray-700 dark:border-gray-600 dark:text-gray-200"
              />
              <button
                  @click="performSearch()"
                  class="ml-2 rounded-sm bg-indigo-500 px-3 py-2 text-sm font-medium text-white hover:bg-indigo-700"
              >
                <MagnifyingGlassIcon class="inline h-4.5 w-4.5"/>
                Search
              </button>

              <button
                  v-if="is_search_active"
                  @click="handle_next_occurrence"
                  class="ml-2 rounded-sm bg-indigo-500 px-3 py-2 text-sm font-medium
                   text-white hover:bg-indigo-700"
              >
                Next Occurrence
              </button>
            </div>
          </div>


          <!-- Loading indicator -->
          <div v-if="logs_loading" class="flex justify-center items-center h-32">
            <p class="text-gray-500 dark:text-gray-400">Loading...</p>
          </div>

          <!-- Log content display -->
          <div v-else class="mt-2 px-2 py-3 sm:p-6 bg-white dark:bg-gray-900">
          <pre
              class="max-h-[70vh] overflow-x-auto whitespace-pre-wrap break-all text-sm text-gray-800 dark:text-gray-200">
            <code id="log-content">
              <template v-if="current_log_file.length > 0 && !is_search_active">
                <span v-for="(line, index) in current_log_file" :key="index">
                  {{ line }}
                </span>
              </template>

              <template v-else-if="is_search_active">
                <span v-for="(line, index) in current_log_file" :key="index"
                      :id="'line-' + index"
                      v-html="highlight(line) + '<br>'"/>
              </template>

              <template v-else>
                Select a log file to view its content.
              </template>
            </code>
          </pre>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style>
@media (max-width: 640px) {
  pre {
    white-space: pre-line;
  }

}
</style>
