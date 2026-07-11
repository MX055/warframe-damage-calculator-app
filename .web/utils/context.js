import { createContext, useContext, useMemo, useReducer, useState, createElement, useEffect } from "react"
import { applyDelta, ReflexEvent, hydrateClientStorage, useEventLoop, refs } from "$/utils/state"
import { jsx } from "@emotion/react";

export const initialState = {"reflex___state____state": {"is_hydrated_rx_state_": false, "router_rx_state_": {"session": {"client_token": "", "client_ip": "", "session_id": ""}, "headers": {"host": "", "origin": "", "upgrade": "", "connection": "", "cookie": "", "pragma": "", "cache_control": "", "user_agent": "", "sec_websocket_version": "", "sec_websocket_key": "", "sec_websocket_extensions": "", "accept_encoding": "", "accept_language": "", "raw_headers": {}}, "page": {"host": "", "path": "", "raw_path": "", "full_path": "", "full_raw_path": "", "params": {}}, "url": "", "route_id": ""}}, "reflex___state____state.reflex___state____frontend_event_exception_state": {}, "reflex___state____state.reflex___state____on_load_internal_state": {}, "reflex___state____state.reflex___state____update_vars_internal_state": {}, "reflex___state____state.warframe_reflex___state____calculator_state": {"arcane_options_rx_state_": ["Custom"], "base_attack_speed_rx_state_": 1.0, "base_burst_count_rx_state_": 1, "base_burst_delay_rx_state_": 0.0, "base_charge_time_rx_state_": 0.0, "base_crit_chance_rx_state_": 0.0, "base_crit_damage_rx_state_": 1.0, "base_fire_rate_rx_state_": 0.05, "base_magazine_capacity_rx_state_": 1, "base_multishot_rx_state_": 1.0, "base_recharge_rate_rx_state_": 0.0, "base_reload_speed_rx_state_": 0.0, "base_status_chance_rx_state_": 0.0, "base_weakpoint_damage_rx_state_": 3.0, "contribution_result_rows_rx_state_": [], "custom_is_bow_rx_state_": false, "custom_weapon_rx_state_": true, "damage_result_rows_rx_state_": [], "direct_damage_fields_rx_state_": [{"name": "impact", "label": "Impact", "value": 0.0, "min_value": 0.0, "max_value": 1000000000.0, "integer": false}, {"name": "puncture", "label": "Puncture", "value": 0.0, "min_value": 0.0, "max_value": 1000000000.0, "integer": false}, {"name": "slash", "label": "Slash", "value": 0.0, "min_value": 0.0, "max_value": 1000000000.0, "integer": false}], "direct_damage_options_rx_state_": [], "direct_damage_pending_rx_state_": "", "exilus_options_rx_state_": ["Custom"], "explosion_damage_fields_rx_state_": [], "explosion_damage_options_rx_state_": [], "explosion_damage_pending_rx_state_": "", "explosion_forced_proc_fields_rx_state_": [], "explosion_forced_proc_options_rx_state_": [], "explosion_forced_proc_pending_rx_state_": "", "external_available_fields_rx_state_": [], "external_fields_rx_state_": [], "external_pending_field_rx_state_": "", "forced_proc_fields_rx_state_": [], "forced_proc_options_rx_state_": [], "forced_proc_pending_rx_state_": "", "has_error_rx_state_": false, "initialized_rx_state_": false, "is_battery_rx_state_": false, "is_beam_rx_state_": false, "is_burst_weapon_rx_state_": false, "is_charge_weapon_rx_state_": false, "main_result_metrics_rx_state_": [], "melee_weapon_rx_state_": false, "misc_result_metrics_rx_state_": [], "mod_options_rx_state_": ["Custom"], "primary_weapon_rx_state_": true, "progenitor_element_rx_state_": "None", "progenitor_value_rx_state_": 0.0, "ranged_weapon_rx_state_": true, "result_contribution_summary_rx_state_": "", "result_error_rx_state_": "", "result_ready_rx_state_": false, "result_summary_rx_state_": "", "selected_weapon_rx_state_": "Custom", "selected_weapon_type_rx_state_": "Primary", "slot_available_fields_rx_state_": [[], [], [], [], [], [], [], [], [], []], "slot_condition_labels_rx_state_": ["", "", "", "", "", "", "", "", "", ""], "slot_conditions_enabled_rx_state_": [true, true, true, true, true, true, true, true, true, true], "slot_contributions_rx_state_": ["—", "—", "—", "—", "—", "—", "—", "—", "—", "—"], "slot_fields_rx_state_": [[], [], [], [], [], [], [], [], [], []], "slot_has_conditionals_rx_state_": [false, false, false, false, false, false, false, false, false, false], "slot_max_ranks_rx_state_": [10, 10, 10, 10, 5, 10, 10, 10, 10, 10], "slot_max_stacks_rx_state_": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0], "slot_pending_fields_rx_state_": ["", "", "", "", "", "", "", "", "", ""], "slot_ranks_rx_state_": [10, 10, 10, 10, 5, 10, 10, 10, 10, 10], "slot_selected_upgrades_rx_state_": ["Custom", "Custom", "Custom", "Custom", "Custom", "Custom", "Custom", "Custom", "Custom", "Custom"], "slot_stacks_rx_state_": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0], "slot_stat_rows_rx_state_": [[], [], [], [], [], [], [], [], [], []], "weakpoint_result_metrics_rx_state_": [], "weapon_options_rx_state_": ["Custom"]}}

export const defaultColorMode = "dark"
export const ColorModeContext = createContext(null);
export const UploadFilesContext = createContext(null);
export const DispatchContext = createContext(null);
export const StateContexts = {reflex___state____state: createContext(null),reflex___state____state__reflex___state____frontend_event_exception_state: createContext(null),reflex___state____state__reflex___state____on_load_internal_state: createContext(null),reflex___state____state__reflex___state____update_vars_internal_state: createContext(null),reflex___state____state__warframe_reflex___state____calculator_state: createContext(null),};
export const EventLoopContext = createContext(null);
export const clientStorage = {"cookies": {}, "local_storage": {}, "session_storage": {}}


export const state_name = "reflex___state____state"

export const exception_state_name = "reflex___state____state.reflex___state____frontend_event_exception_state"

// These events are triggered on initial load and each page navigation.
export const onLoadInternalEvent = () => {
    const internal_events = [];

    // Get tracked cookie and local storage vars to send to the backend.
    const client_storage_vars = hydrateClientStorage(clientStorage);
    // But only send the vars if any are actually set in the browser.
    if (client_storage_vars && Object.keys(client_storage_vars).length !== 0) {
        internal_events.push(
            ReflexEvent(
                'reflex___state____state.reflex___state____update_vars_internal_state.update_vars_internal',
                {vars: client_storage_vars},
            ),
        );
    }

    // `on_load_internal` triggers the correct on_load event(s) for the current page.
    // If the page does not define any on_load event, this will just set `is_hydrated = true`.
    internal_events.push(ReflexEvent('reflex___state____state.reflex___state____on_load_internal_state.on_load_internal'));

    return internal_events;
}

// The following events are sent when the websocket connects or reconnects.
export const initialEvents = () => [
    ReflexEvent('reflex___state____state.hydrate'),
    ...onLoadInternalEvent()
]
    

export const isDevMode = true;

export function UploadFilesProvider({ children }) {
  const [filesById, setFilesById] = useState({})
  refs["__clear_selected_files"] = (id) => setFilesById(filesById => {
    const newFilesById = {...filesById}
    delete newFilesById[id]
    return newFilesById
  })
  return createElement(
    UploadFilesContext.Provider,
    { value: [filesById, setFilesById] },
    children
  );
}

export function ClientSide(component) {
  return ({ children, ...props }) => {
    const [Component, setComponent] = useState(null);
    useEffect(() => {
      async function load() {
        const comp = await component();
        setComponent(() => comp);
      }
      load();
    }, []);
    return Component ? jsx(Component, props, children) : null;
  };
}

export function EventLoopProvider({ children }) {
  const dispatch = useContext(DispatchContext)
  const [addEvents, connectErrors] = useEventLoop(
    dispatch,
    initialEvents,
    clientStorage,
  )
  return createElement(
    EventLoopContext.Provider,
    { value: [addEvents, connectErrors] },
    children
  );
}

export function StateProvider({ children }) {
  const [reflex___state____state, dispatch_reflex___state____state] = useReducer(applyDelta, initialState["reflex___state____state"])
const [reflex___state____state__reflex___state____frontend_event_exception_state, dispatch_reflex___state____state__reflex___state____frontend_event_exception_state] = useReducer(applyDelta, initialState["reflex___state____state.reflex___state____frontend_event_exception_state"])
const [reflex___state____state__reflex___state____on_load_internal_state, dispatch_reflex___state____state__reflex___state____on_load_internal_state] = useReducer(applyDelta, initialState["reflex___state____state.reflex___state____on_load_internal_state"])
const [reflex___state____state__reflex___state____update_vars_internal_state, dispatch_reflex___state____state__reflex___state____update_vars_internal_state] = useReducer(applyDelta, initialState["reflex___state____state.reflex___state____update_vars_internal_state"])
const [reflex___state____state__warframe_reflex___state____calculator_state, dispatch_reflex___state____state__warframe_reflex___state____calculator_state] = useReducer(applyDelta, initialState["reflex___state____state.warframe_reflex___state____calculator_state"])
  const dispatchers = useMemo(() => {
    return {
      "reflex___state____state": dispatch_reflex___state____state,
"reflex___state____state.reflex___state____frontend_event_exception_state": dispatch_reflex___state____state__reflex___state____frontend_event_exception_state,
"reflex___state____state.reflex___state____on_load_internal_state": dispatch_reflex___state____state__reflex___state____on_load_internal_state,
"reflex___state____state.reflex___state____update_vars_internal_state": dispatch_reflex___state____state__reflex___state____update_vars_internal_state,
"reflex___state____state.warframe_reflex___state____calculator_state": dispatch_reflex___state____state__warframe_reflex___state____calculator_state,
    }
  }, [])

  return (
    createElement(StateContexts.reflex___state____state,{value: reflex___state____state},
createElement(StateContexts.reflex___state____state__reflex___state____frontend_event_exception_state,{value: reflex___state____state__reflex___state____frontend_event_exception_state},
createElement(StateContexts.reflex___state____state__reflex___state____on_load_internal_state,{value: reflex___state____state__reflex___state____on_load_internal_state},
createElement(StateContexts.reflex___state____state__reflex___state____update_vars_internal_state,{value: reflex___state____state__reflex___state____update_vars_internal_state},
createElement(StateContexts.reflex___state____state__warframe_reflex___state____calculator_state,{value: reflex___state____state__warframe_reflex___state____calculator_state},
    createElement(DispatchContext, {value: dispatchers}, children)
    )))))
  )
}