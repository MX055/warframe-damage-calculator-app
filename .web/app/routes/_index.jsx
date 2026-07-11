import {Fragment,useCallback,useContext,useEffect} from "react"
import {Badge as RadixThemesBadge,Box as RadixThemesBox,Button as RadixThemesButton,Checkbox as RadixThemesCheckbox,Code as RadixThemesCode,Flex as RadixThemesFlex,Grid as RadixThemesGrid,Heading as RadixThemesHeading,Link as RadixThemesLink,Select as RadixThemesSelect,Separator as RadixThemesSeparator,Switch as RadixThemesSwitch,Table as RadixThemesTable,Tabs as RadixThemesTabs,Text as RadixThemesText,TextField as RadixThemesTextField} from "@radix-ui/themes"
import {Content as RadixAccordionContent,Header as RadixAccordionHeader,Item as RadixAccordionItem,Root as RadixAccordionRoot,Trigger as RadixAccordionTrigger} from "@radix-ui/react-accordion"
import {ChevronDown as LucideChevronDown} from "lucide-react"
import {jsx,keyframes} from "@emotion/react"
import {Link as ReactRouterLink} from "react-router"
import {ReflexEvent,isNotNullOrUndefined,isTrue} from "$/utils/state"
import {ColorModeContext,EventLoopContext,StateContexts} from "$/utils/context"
import DebounceInput from "react-debounce-input"
import {PrismAsyncLight as SyntaxHighlighter} from "react-syntax-highlighter"
import oneLight from "react-syntax-highlighter/dist/esm/styles/prism/one-light"
import oneDark from "react-syntax-highlighter/dist/esm/styles/prism/one-dark"




function Select__root_0b867d07f7089935bcae2ccfe2884636 () {
  const reflex___state____state__warframe_reflex___state____calculator_state = useContext(StateContexts.reflex___state____state__warframe_reflex___state____calculator_state)
const [addEvents, connectErrors] = useContext(EventLoopContext);

const on_change_08a78ffb2e9b316cf384f1f116390f41 = useCallback(((_ev_0) => (addEvents([(ReflexEvent("reflex___state____state.warframe_reflex___state____calculator_state.set_weapon_type", ({ ["value"] : _ev_0 }), ({  })))], [_ev_0], ({  })))), [addEvents, ReflexEvent])

  return (
    jsx(RadixThemesSelect.Root,{disabled:false,onValueChange:on_change_08a78ffb2e9b316cf384f1f116390f41,value:reflex___state____state__warframe_reflex___state____calculator_state.selected_weapon_type_rx_state_},jsx(RadixThemesSelect.Trigger,{css:({ ["width"] : "100%" })},),jsx(RadixThemesSelect.Content,{position:"popper"},jsx(RadixThemesSelect.Group,{},"",jsx(RadixThemesSelect.Item,{value:"Melee"},"Melee"),jsx(RadixThemesSelect.Item,{value:"Primary"},"Primary"),jsx(RadixThemesSelect.Item,{value:"Secondary"},"Secondary"))))
  )
}


function Select__group_c0031851c5487667d588b80b9ef9bdf4 () {
  const reflex___state____state__warframe_reflex___state____calculator_state = useContext(StateContexts.reflex___state____state__warframe_reflex___state____calculator_state)



  return (
    jsx(RadixThemesSelect.Group,{},"",Array.prototype.map.call(reflex___state____state__warframe_reflex___state____calculator_state.weapon_options_rx_state_ ?? [],((item_rx_state_,index_d6d6157c99650830f12a866606ea87b7)=>(jsx(RadixThemesSelect.Item,{key:index_d6d6157c99650830f12a866606ea87b7,value:item_rx_state_},item_rx_state_)))))
  )
}


function Select__root_4b29509caa1269fca3cd82330720fee9 () {
  const reflex___state____state__warframe_reflex___state____calculator_state = useContext(StateContexts.reflex___state____state__warframe_reflex___state____calculator_state)
const [addEvents, connectErrors] = useContext(EventLoopContext);

const on_change_f563d1d633d29e03414f1282f8529f44 = useCallback(((_ev_0) => (addEvents([(ReflexEvent("reflex___state____state.warframe_reflex___state____calculator_state.set_weapon", ({ ["value"] : _ev_0 }), ({  })))], [_ev_0], ({  })))), [addEvents, ReflexEvent])

  return (
    jsx(RadixThemesSelect.Root,{disabled:false,onValueChange:on_change_f563d1d633d29e03414f1282f8529f44,value:reflex___state____state__warframe_reflex___state____calculator_state.selected_weapon_rx_state_},jsx(RadixThemesSelect.Trigger,{css:({ ["width"] : "100%" })},),jsx(RadixThemesSelect.Content,{position:"popper"},jsx(Select__group_c0031851c5487667d588b80b9ef9bdf4,{},)))
  )
}


function Switch_4711c813253df86a5971e957727a99c8 () {
  const reflex___state____state__warframe_reflex___state____calculator_state = useContext(StateContexts.reflex___state____state__warframe_reflex___state____calculator_state)
const [addEvents, connectErrors] = useContext(EventLoopContext);

const on_change_15656e159f73521ae9aa23ed2ea50f05 = useCallback(((_ev_0) => (addEvents([(ReflexEvent("reflex___state____state.warframe_reflex___state____calculator_state.set_base_toggle", ({ ["field_name"] : "is_battery", ["value"] : _ev_0 }), ({  })))], [_ev_0], ({  })))), [addEvents, ReflexEvent])

  return (
    jsx(RadixThemesSwitch,{checked:reflex___state____state__warframe_reflex___state____calculator_state.is_battery_rx_state_,onCheckedChange:on_change_15656e159f73521ae9aa23ed2ea50f05},)
  )
}


function Switch_fb3a4575fb268dda867cc0e204e33dd5 () {
  const reflex___state____state__warframe_reflex___state____calculator_state = useContext(StateContexts.reflex___state____state__warframe_reflex___state____calculator_state)
const [addEvents, connectErrors] = useContext(EventLoopContext);

const on_change_c5c585e0767754ba45313fdb91a197ca = useCallback(((_ev_0) => (addEvents([(ReflexEvent("reflex___state____state.warframe_reflex___state____calculator_state.set_base_toggle", ({ ["field_name"] : "is_charge_weapon", ["value"] : _ev_0 }), ({  })))], [_ev_0], ({  })))), [addEvents, ReflexEvent])

  return (
    jsx(RadixThemesSwitch,{checked:reflex___state____state__warframe_reflex___state____calculator_state.is_charge_weapon_rx_state_,onCheckedChange:on_change_c5c585e0767754ba45313fdb91a197ca},)
  )
}


function Switch_191827c43da6a18397a9b1cec678a1d9 () {
  const reflex___state____state__warframe_reflex___state____calculator_state = useContext(StateContexts.reflex___state____state__warframe_reflex___state____calculator_state)
const [addEvents, connectErrors] = useContext(EventLoopContext);

const on_change_10836522bab6aaa07a386e46b077f15b = useCallback(((_ev_0) => (addEvents([(ReflexEvent("reflex___state____state.warframe_reflex___state____calculator_state.set_base_toggle", ({ ["field_name"] : "is_burst_weapon", ["value"] : _ev_0 }), ({  })))], [_ev_0], ({  })))), [addEvents, ReflexEvent])

  return (
    jsx(RadixThemesSwitch,{checked:reflex___state____state__warframe_reflex___state____calculator_state.is_burst_weapon_rx_state_,onCheckedChange:on_change_10836522bab6aaa07a386e46b077f15b},)
  )
}


function Switch_74aca291819dcb7386b5d7306432d175 () {
  const reflex___state____state__warframe_reflex___state____calculator_state = useContext(StateContexts.reflex___state____state__warframe_reflex___state____calculator_state)
const [addEvents, connectErrors] = useContext(EventLoopContext);

const on_change_9ce27dc2f76b41d8ef0b317ed38aa437 = useCallback(((_ev_0) => (addEvents([(ReflexEvent("reflex___state____state.warframe_reflex___state____calculator_state.set_base_toggle", ({ ["field_name"] : "is_beam", ["value"] : _ev_0 }), ({  })))], [_ev_0], ({  })))), [addEvents, ReflexEvent])

  return (
    jsx(RadixThemesSwitch,{checked:reflex___state____state__warframe_reflex___state____calculator_state.is_beam_rx_state_,onCheckedChange:on_change_9ce27dc2f76b41d8ef0b317ed38aa437},)
  )
}


function Switch_778a86987571dd8ee2baecbf35037169 () {
  const reflex___state____state__warframe_reflex___state____calculator_state = useContext(StateContexts.reflex___state____state__warframe_reflex___state____calculator_state)
const [addEvents, connectErrors] = useContext(EventLoopContext);

const on_change_0707ca3bf94c12b0e875b698211a3d7a = useCallback(((_ev_0) => (addEvents([(ReflexEvent("reflex___state____state.warframe_reflex___state____calculator_state.set_base_toggle", ({ ["field_name"] : "custom_is_bow", ["value"] : _ev_0 }), ({  })))], [_ev_0], ({  })))), [addEvents, ReflexEvent])

  return (
    jsx(RadixThemesSwitch,{checked:reflex___state____state__warframe_reflex___state____calculator_state.custom_is_bow_rx_state_,onCheckedChange:on_change_0707ca3bf94c12b0e875b698211a3d7a},)
  )
}


function Fragment_f288230fa69ce6b4a421d17abf756aff () {
  const reflex___state____state__warframe_reflex___state____calculator_state = useContext(StateContexts.reflex___state____state__warframe_reflex___state____calculator_state)



  return (
    jsx(Fragment,{},(reflex___state____state__warframe_reflex___state____calculator_state.primary_weapon_rx_state_?(jsx(Fragment,{},jsx(RadixThemesFlex,{align:"center",className:"rx-Stack toggle-control",css:({ ["width"] : "100%" }),direction:"row",gap:"3"},jsx(RadixThemesText,{as:"p",className:"toggle-label"},"Bow"),jsx(RadixThemesFlex,{css:({ ["flex"] : 1, ["justifySelf"] : "stretch", ["alignSelf"] : "stretch" })},),jsx(Switch_778a86987571dd8ee2baecbf35037169,{},)))):(jsx(Fragment,{},))))
  )
}


function Fragment_af1ebccbd20d0f03f339f2b75d67b3ff () {
  const reflex___state____state__warframe_reflex___state____calculator_state = useContext(StateContexts.reflex___state____state__warframe_reflex___state____calculator_state)



  return (
    jsx(Fragment,{},(reflex___state____state__warframe_reflex___state____calculator_state.ranged_weapon_rx_state_?(jsx(Fragment,{},jsx(RadixThemesGrid,{className:"form-grid form-grid-5",columns:({ ["initial"] : "1", ["sm"] : "2", ["lg"] : "5" }),css:({ ["gap"] : "3", ["width"] : "100%" })},jsx(RadixThemesFlex,{align:"center",className:"rx-Stack toggle-control",css:({ ["width"] : "100%" }),direction:"row",gap:"3"},jsx(RadixThemesText,{as:"p",className:"toggle-label"},"Battery Weapon"),jsx(RadixThemesFlex,{css:({ ["flex"] : 1, ["justifySelf"] : "stretch", ["alignSelf"] : "stretch" })},),jsx(Switch_4711c813253df86a5971e957727a99c8,{},)),jsx(RadixThemesFlex,{align:"center",className:"rx-Stack toggle-control",css:({ ["width"] : "100%" }),direction:"row",gap:"3"},jsx(RadixThemesText,{as:"p",className:"toggle-label"},"Charge Weapon"),jsx(RadixThemesFlex,{css:({ ["flex"] : 1, ["justifySelf"] : "stretch", ["alignSelf"] : "stretch" })},),jsx(Switch_fb3a4575fb268dda867cc0e204e33dd5,{},)),jsx(RadixThemesFlex,{align:"center",className:"rx-Stack toggle-control",css:({ ["width"] : "100%" }),direction:"row",gap:"3"},jsx(RadixThemesText,{as:"p",className:"toggle-label"},"Burst Weapon"),jsx(RadixThemesFlex,{css:({ ["flex"] : 1, ["justifySelf"] : "stretch", ["alignSelf"] : "stretch" })},),jsx(Switch_191827c43da6a18397a9b1cec678a1d9,{},)),jsx(RadixThemesFlex,{align:"center",className:"rx-Stack toggle-control",css:({ ["width"] : "100%" }),direction:"row",gap:"3"},jsx(RadixThemesText,{as:"p",className:"toggle-label"},"Beam Weapon"),jsx(RadixThemesFlex,{css:({ ["flex"] : 1, ["justifySelf"] : "stretch", ["alignSelf"] : "stretch" })},),jsx(Switch_74aca291819dcb7386b5d7306432d175,{},)),jsx(Fragment_f288230fa69ce6b4a421d17abf756aff,{},)))):(jsx(Fragment,{},))))
  )
}


function Select__group_388a31f5c4e67b332ecddf11cd0aba5a () {
  const reflex___state____state__warframe_reflex___state____calculator_state = useContext(StateContexts.reflex___state____state__warframe_reflex___state____calculator_state)



  return (
    jsx(RadixThemesSelect.Group,{},"",Array.prototype.map.call(reflex___state____state__warframe_reflex___state____calculator_state.direct_damage_options_rx_state_ ?? [],((item_rx_state_,index_d6d6157c99650830f12a866606ea87b7)=>(jsx(RadixThemesSelect.Item,{key:index_d6d6157c99650830f12a866606ea87b7,value:item_rx_state_},item_rx_state_)))))
  )
}


function Select__root_b34cfbe1c68a9b79f1867a236cb0f77b () {
  const reflex___state____state__warframe_reflex___state____calculator_state = useContext(StateContexts.reflex___state____state__warframe_reflex___state____calculator_state)
const [addEvents, connectErrors] = useContext(EventLoopContext);

const on_change_6526c7e720c663b80d3ef4bebda449bc = useCallback(((_ev_0) => (addEvents([(ReflexEvent("reflex___state____state.warframe_reflex___state____calculator_state.set_damage_pending", ({ ["group"] : "direct_damage", ["value"] : _ev_0 }), ({  })))], [_ev_0], ({  })))), [addEvents, ReflexEvent])

  return (
    jsx(RadixThemesSelect.Root,{disabled:(reflex___state____state__warframe_reflex___state____calculator_state.direct_damage_options_rx_state_.length?.valueOf?.() === 0?.valueOf?.()),onValueChange:on_change_6526c7e720c663b80d3ef4bebda449bc,value:reflex___state____state__warframe_reflex___state____calculator_state.direct_damage_pending_rx_state_},jsx(RadixThemesSelect.Trigger,{css:({ ["width"] : "100%" })},),jsx(RadixThemesSelect.Content,{position:"popper"},jsx(Select__group_388a31f5c4e67b332ecddf11cd0aba5a,{},)))
  )
}


function Button_268537da38ed2e5ba5c26342b7c13d89 () {
  const reflex___state____state__warframe_reflex___state____calculator_state = useContext(StateContexts.reflex___state____state__warframe_reflex___state____calculator_state)
const [addEvents, connectErrors] = useContext(EventLoopContext);

const on_click_e4cc072e783995b1968022803e7f3af8 = useCallback(((_e) => (addEvents([(ReflexEvent("reflex___state____state.warframe_reflex___state____calculator_state.add_damage_type", ({ ["group"] : "direct_damage" }), ({  })))], [_e], ({  })))), [addEvents, ReflexEvent])

  return (
    jsx(RadixThemesButton,{className:"icon-button",disabled:(reflex___state____state__warframe_reflex___state____calculator_state.direct_damage_options_rx_state_.length?.valueOf?.() === 0?.valueOf?.()),onClick:on_click_e4cc072e783995b1968022803e7f3af8},"+")
  )
}


function Flex_7324869fbc42cf7fc93b63c0bbd08647 () {
  const reflex___state____state__warframe_reflex___state____calculator_state = useContext(StateContexts.reflex___state____state__warframe_reflex___state____calculator_state)
const [addEvents, connectErrors] = useContext(EventLoopContext);



  return (
    jsx(RadixThemesFlex,{align:"start",className:"rx-Stack",css:({ ["width"] : "100%", ["gap"] : "2" }),direction:"column",gap:"3"},Array.prototype.map.call(reflex___state____state__warframe_reflex___state____calculator_state.direct_damage_fields_rx_state_ ?? [],((field_rx_state_,index_ad9d7b81e0e65a5948a3885101cbe585)=>(jsx(RadixThemesGrid,{align:"center",columns:"76px minmax(0, 1fr) 32px",css:({ ["columnGap"] : "8px", ["width"] : "100%" }),key:index_ad9d7b81e0e65a5948a3885101cbe585},jsx(RadixThemesText,{as:"p",className:"compact-label"},field_rx_state_?.["label"]),jsx(DebounceInput,{css:({ ["debounceTimeout"] : 250, ["width"] : "100%" }),debounceTimeout:250,element:RadixThemesTextField.Root,min:0,onChange:((_e) => (addEvents([(ReflexEvent("reflex___state____state.warframe_reflex___state____calculator_state.set_damage_value", ({ ["group"] : "direct_damage", ["damage_name"] : field_rx_state_?.["name"], ["value"] : _e?.["target"]?.["value"] }), ({  })))], [_e], ({  })))),step:"0.001",type:"number",value:(isNotNullOrUndefined(field_rx_state_?.["value"]) ? field_rx_state_?.["value"] : "")},),jsx(RadixThemesButton,{className:"icon-button",onClick:((_e) => (addEvents([(ReflexEvent("reflex___state____state.warframe_reflex___state____calculator_state.remove_damage_type", ({ ["group"] : "direct_damage", ["damage_name"] : field_rx_state_?.["name"] }), ({  })))], [_e], ({  })))),variant:"soft"},"\u00d7"))))))
  )
}


function Fragment_a7acf6cd05dce15c01ad7655ec9a7806 () {
  const reflex___state____state__warframe_reflex___state____calculator_state = useContext(StateContexts.reflex___state____state__warframe_reflex___state____calculator_state)



  return (
    jsx(Fragment,{},((reflex___state____state__warframe_reflex___state____calculator_state.direct_damage_fields_rx_state_.length > 0)?(jsx(Fragment,{},jsx(Flex_7324869fbc42cf7fc93b63c0bbd08647,{},))):(jsx(Fragment,{},jsx(RadixThemesText,{as:"p",className:"empty-text"},"No damage types added.")))))
  )
}


function Select__group_c116729d37044779b798107996422d0b () {
  const reflex___state____state__warframe_reflex___state____calculator_state = useContext(StateContexts.reflex___state____state__warframe_reflex___state____calculator_state)



  return (
    jsx(RadixThemesSelect.Group,{},"",Array.prototype.map.call(reflex___state____state__warframe_reflex___state____calculator_state.forced_proc_options_rx_state_ ?? [],((item_rx_state_,index_d6d6157c99650830f12a866606ea87b7)=>(jsx(RadixThemesSelect.Item,{key:index_d6d6157c99650830f12a866606ea87b7,value:item_rx_state_},item_rx_state_)))))
  )
}


function Select__root_a2bb3f1fafd729b0f88cf15ede2297e3 () {
  const reflex___state____state__warframe_reflex___state____calculator_state = useContext(StateContexts.reflex___state____state__warframe_reflex___state____calculator_state)
const [addEvents, connectErrors] = useContext(EventLoopContext);

const on_change_53aa7eb0f7b8206e445dccce67fecf01 = useCallback(((_ev_0) => (addEvents([(ReflexEvent("reflex___state____state.warframe_reflex___state____calculator_state.set_damage_pending", ({ ["group"] : "forced_proc", ["value"] : _ev_0 }), ({  })))], [_ev_0], ({  })))), [addEvents, ReflexEvent])

  return (
    jsx(RadixThemesSelect.Root,{disabled:(reflex___state____state__warframe_reflex___state____calculator_state.forced_proc_options_rx_state_.length?.valueOf?.() === 0?.valueOf?.()),onValueChange:on_change_53aa7eb0f7b8206e445dccce67fecf01,value:reflex___state____state__warframe_reflex___state____calculator_state.forced_proc_pending_rx_state_},jsx(RadixThemesSelect.Trigger,{css:({ ["width"] : "100%" })},),jsx(RadixThemesSelect.Content,{position:"popper"},jsx(Select__group_c116729d37044779b798107996422d0b,{},)))
  )
}


function Button_ad15771136b3037e79e2dca71cfb7b8a () {
  const reflex___state____state__warframe_reflex___state____calculator_state = useContext(StateContexts.reflex___state____state__warframe_reflex___state____calculator_state)
const [addEvents, connectErrors] = useContext(EventLoopContext);

const on_click_11c379565f901f37788d228ea7494275 = useCallback(((_e) => (addEvents([(ReflexEvent("reflex___state____state.warframe_reflex___state____calculator_state.add_damage_type", ({ ["group"] : "forced_proc" }), ({  })))], [_e], ({  })))), [addEvents, ReflexEvent])

  return (
    jsx(RadixThemesButton,{className:"icon-button",disabled:(reflex___state____state__warframe_reflex___state____calculator_state.forced_proc_options_rx_state_.length?.valueOf?.() === 0?.valueOf?.()),onClick:on_click_11c379565f901f37788d228ea7494275},"+")
  )
}


function Flex_f06bf357f57a362afda814b54adbfa37 () {
  const reflex___state____state__warframe_reflex___state____calculator_state = useContext(StateContexts.reflex___state____state__warframe_reflex___state____calculator_state)
const [addEvents, connectErrors] = useContext(EventLoopContext);



  return (
    jsx(RadixThemesFlex,{align:"start",className:"rx-Stack",css:({ ["width"] : "100%", ["gap"] : "2" }),direction:"column",gap:"3"},Array.prototype.map.call(reflex___state____state__warframe_reflex___state____calculator_state.forced_proc_fields_rx_state_ ?? [],((field_rx_state_,index_ad9d7b81e0e65a5948a3885101cbe585)=>(jsx(RadixThemesGrid,{align:"center",columns:"76px minmax(0, 1fr) 32px",css:({ ["columnGap"] : "8px", ["width"] : "100%" }),key:index_ad9d7b81e0e65a5948a3885101cbe585},jsx(RadixThemesText,{as:"p",className:"compact-label"},field_rx_state_?.["label"]),jsx(DebounceInput,{css:({ ["debounceTimeout"] : 250, ["width"] : "100%" }),debounceTimeout:250,element:RadixThemesTextField.Root,min:0,onChange:((_e) => (addEvents([(ReflexEvent("reflex___state____state.warframe_reflex___state____calculator_state.set_damage_value", ({ ["group"] : "forced_proc", ["damage_name"] : field_rx_state_?.["name"], ["value"] : _e?.["target"]?.["value"] }), ({  })))], [_e], ({  })))),step:"0.001",type:"number",value:(isNotNullOrUndefined(field_rx_state_?.["value"]) ? field_rx_state_?.["value"] : "")},),jsx(RadixThemesButton,{className:"icon-button",onClick:((_e) => (addEvents([(ReflexEvent("reflex___state____state.warframe_reflex___state____calculator_state.remove_damage_type", ({ ["group"] : "forced_proc", ["damage_name"] : field_rx_state_?.["name"] }), ({  })))], [_e], ({  })))),variant:"soft"},"\u00d7"))))))
  )
}


function Fragment_691cf2eb67157c3e06261e8d17c14f20 () {
  const reflex___state____state__warframe_reflex___state____calculator_state = useContext(StateContexts.reflex___state____state__warframe_reflex___state____calculator_state)



  return (
    jsx(Fragment,{},((reflex___state____state__warframe_reflex___state____calculator_state.forced_proc_fields_rx_state_.length > 0)?(jsx(Fragment,{},jsx(Flex_f06bf357f57a362afda814b54adbfa37,{},))):(jsx(Fragment,{},jsx(RadixThemesText,{as:"p",className:"empty-text"},"No damage types added.")))))
  )
}


function Select__group_60a3fe32f8d177c1f638a046547c8b9e () {
  const reflex___state____state__warframe_reflex___state____calculator_state = useContext(StateContexts.reflex___state____state__warframe_reflex___state____calculator_state)



  return (
    jsx(RadixThemesSelect.Group,{},"",Array.prototype.map.call(reflex___state____state__warframe_reflex___state____calculator_state.explosion_damage_options_rx_state_ ?? [],((item_rx_state_,index_d6d6157c99650830f12a866606ea87b7)=>(jsx(RadixThemesSelect.Item,{key:index_d6d6157c99650830f12a866606ea87b7,value:item_rx_state_},item_rx_state_)))))
  )
}


function Select__root_99aeef4d268bca4723df429e37ea04fd () {
  const reflex___state____state__warframe_reflex___state____calculator_state = useContext(StateContexts.reflex___state____state__warframe_reflex___state____calculator_state)
const [addEvents, connectErrors] = useContext(EventLoopContext);

const on_change_560cb8058787a693484cbeb36e819d05 = useCallback(((_ev_0) => (addEvents([(ReflexEvent("reflex___state____state.warframe_reflex___state____calculator_state.set_damage_pending", ({ ["group"] : "explosion_damage", ["value"] : _ev_0 }), ({  })))], [_ev_0], ({  })))), [addEvents, ReflexEvent])

  return (
    jsx(RadixThemesSelect.Root,{disabled:(reflex___state____state__warframe_reflex___state____calculator_state.explosion_damage_options_rx_state_.length?.valueOf?.() === 0?.valueOf?.()),onValueChange:on_change_560cb8058787a693484cbeb36e819d05,value:reflex___state____state__warframe_reflex___state____calculator_state.explosion_damage_pending_rx_state_},jsx(RadixThemesSelect.Trigger,{css:({ ["width"] : "100%" })},),jsx(RadixThemesSelect.Content,{position:"popper"},jsx(Select__group_60a3fe32f8d177c1f638a046547c8b9e,{},)))
  )
}


function Button_4bfb4b7408e884eba39534fcc0214214 () {
  const reflex___state____state__warframe_reflex___state____calculator_state = useContext(StateContexts.reflex___state____state__warframe_reflex___state____calculator_state)
const [addEvents, connectErrors] = useContext(EventLoopContext);

const on_click_74aaeca3be41f9925c3e11d51dae9b5e = useCallback(((_e) => (addEvents([(ReflexEvent("reflex___state____state.warframe_reflex___state____calculator_state.add_damage_type", ({ ["group"] : "explosion_damage" }), ({  })))], [_e], ({  })))), [addEvents, ReflexEvent])

  return (
    jsx(RadixThemesButton,{className:"icon-button",disabled:(reflex___state____state__warframe_reflex___state____calculator_state.explosion_damage_options_rx_state_.length?.valueOf?.() === 0?.valueOf?.()),onClick:on_click_74aaeca3be41f9925c3e11d51dae9b5e},"+")
  )
}


function Flex_efa8b061d72853cafef852f8801acaad () {
  const reflex___state____state__warframe_reflex___state____calculator_state = useContext(StateContexts.reflex___state____state__warframe_reflex___state____calculator_state)
const [addEvents, connectErrors] = useContext(EventLoopContext);



  return (
    jsx(RadixThemesFlex,{align:"start",className:"rx-Stack",css:({ ["width"] : "100%", ["gap"] : "2" }),direction:"column",gap:"3"},Array.prototype.map.call(reflex___state____state__warframe_reflex___state____calculator_state.explosion_damage_fields_rx_state_ ?? [],((field_rx_state_,index_ad9d7b81e0e65a5948a3885101cbe585)=>(jsx(RadixThemesGrid,{align:"center",columns:"76px minmax(0, 1fr) 32px",css:({ ["columnGap"] : "8px", ["width"] : "100%" }),key:index_ad9d7b81e0e65a5948a3885101cbe585},jsx(RadixThemesText,{as:"p",className:"compact-label"},field_rx_state_?.["label"]),jsx(DebounceInput,{css:({ ["debounceTimeout"] : 250, ["width"] : "100%" }),debounceTimeout:250,element:RadixThemesTextField.Root,min:0,onChange:((_e) => (addEvents([(ReflexEvent("reflex___state____state.warframe_reflex___state____calculator_state.set_damage_value", ({ ["group"] : "explosion_damage", ["damage_name"] : field_rx_state_?.["name"], ["value"] : _e?.["target"]?.["value"] }), ({  })))], [_e], ({  })))),step:"0.001",type:"number",value:(isNotNullOrUndefined(field_rx_state_?.["value"]) ? field_rx_state_?.["value"] : "")},),jsx(RadixThemesButton,{className:"icon-button",onClick:((_e) => (addEvents([(ReflexEvent("reflex___state____state.warframe_reflex___state____calculator_state.remove_damage_type", ({ ["group"] : "explosion_damage", ["damage_name"] : field_rx_state_?.["name"] }), ({  })))], [_e], ({  })))),variant:"soft"},"\u00d7"))))))
  )
}


function Fragment_d812a4d7a33bcc63223181e7376c86cc () {
  const reflex___state____state__warframe_reflex___state____calculator_state = useContext(StateContexts.reflex___state____state__warframe_reflex___state____calculator_state)



  return (
    jsx(Fragment,{},((reflex___state____state__warframe_reflex___state____calculator_state.explosion_damage_fields_rx_state_.length > 0)?(jsx(Fragment,{},jsx(Flex_efa8b061d72853cafef852f8801acaad,{},))):(jsx(Fragment,{},jsx(RadixThemesText,{as:"p",className:"empty-text"},"No damage types added.")))))
  )
}


function Select__group_4c573e39e3e97a78eaa85542b212a068 () {
  const reflex___state____state__warframe_reflex___state____calculator_state = useContext(StateContexts.reflex___state____state__warframe_reflex___state____calculator_state)



  return (
    jsx(RadixThemesSelect.Group,{},"",Array.prototype.map.call(reflex___state____state__warframe_reflex___state____calculator_state.explosion_forced_proc_options_rx_state_ ?? [],((item_rx_state_,index_d6d6157c99650830f12a866606ea87b7)=>(jsx(RadixThemesSelect.Item,{key:index_d6d6157c99650830f12a866606ea87b7,value:item_rx_state_},item_rx_state_)))))
  )
}


function Select__root_89537645737e9323b096c1771d9f8cff () {
  const reflex___state____state__warframe_reflex___state____calculator_state = useContext(StateContexts.reflex___state____state__warframe_reflex___state____calculator_state)
const [addEvents, connectErrors] = useContext(EventLoopContext);

const on_change_d557bec9f304d5e7e525127e5e6e2bb0 = useCallback(((_ev_0) => (addEvents([(ReflexEvent("reflex___state____state.warframe_reflex___state____calculator_state.set_damage_pending", ({ ["group"] : "explosion_forced_proc", ["value"] : _ev_0 }), ({  })))], [_ev_0], ({  })))), [addEvents, ReflexEvent])

  return (
    jsx(RadixThemesSelect.Root,{disabled:(reflex___state____state__warframe_reflex___state____calculator_state.explosion_forced_proc_options_rx_state_.length?.valueOf?.() === 0?.valueOf?.()),onValueChange:on_change_d557bec9f304d5e7e525127e5e6e2bb0,value:reflex___state____state__warframe_reflex___state____calculator_state.explosion_forced_proc_pending_rx_state_},jsx(RadixThemesSelect.Trigger,{css:({ ["width"] : "100%" })},),jsx(RadixThemesSelect.Content,{position:"popper"},jsx(Select__group_4c573e39e3e97a78eaa85542b212a068,{},)))
  )
}


function Button_afbfa04c6516a8fb2be92ce58cb9d39a () {
  const reflex___state____state__warframe_reflex___state____calculator_state = useContext(StateContexts.reflex___state____state__warframe_reflex___state____calculator_state)
const [addEvents, connectErrors] = useContext(EventLoopContext);

const on_click_9fa9cb0789c3445b8f7212345734e97e = useCallback(((_e) => (addEvents([(ReflexEvent("reflex___state____state.warframe_reflex___state____calculator_state.add_damage_type", ({ ["group"] : "explosion_forced_proc" }), ({  })))], [_e], ({  })))), [addEvents, ReflexEvent])

  return (
    jsx(RadixThemesButton,{className:"icon-button",disabled:(reflex___state____state__warframe_reflex___state____calculator_state.explosion_forced_proc_options_rx_state_.length?.valueOf?.() === 0?.valueOf?.()),onClick:on_click_9fa9cb0789c3445b8f7212345734e97e},"+")
  )
}


function Flex_883b15394fa8cdd4dc0a40f86c041fe7 () {
  const reflex___state____state__warframe_reflex___state____calculator_state = useContext(StateContexts.reflex___state____state__warframe_reflex___state____calculator_state)
const [addEvents, connectErrors] = useContext(EventLoopContext);



  return (
    jsx(RadixThemesFlex,{align:"start",className:"rx-Stack",css:({ ["width"] : "100%", ["gap"] : "2" }),direction:"column",gap:"3"},Array.prototype.map.call(reflex___state____state__warframe_reflex___state____calculator_state.explosion_forced_proc_fields_rx_state_ ?? [],((field_rx_state_,index_ad9d7b81e0e65a5948a3885101cbe585)=>(jsx(RadixThemesGrid,{align:"center",columns:"76px minmax(0, 1fr) 32px",css:({ ["columnGap"] : "8px", ["width"] : "100%" }),key:index_ad9d7b81e0e65a5948a3885101cbe585},jsx(RadixThemesText,{as:"p",className:"compact-label"},field_rx_state_?.["label"]),jsx(DebounceInput,{css:({ ["debounceTimeout"] : 250, ["width"] : "100%" }),debounceTimeout:250,element:RadixThemesTextField.Root,min:0,onChange:((_e) => (addEvents([(ReflexEvent("reflex___state____state.warframe_reflex___state____calculator_state.set_damage_value", ({ ["group"] : "explosion_forced_proc", ["damage_name"] : field_rx_state_?.["name"], ["value"] : _e?.["target"]?.["value"] }), ({  })))], [_e], ({  })))),step:"0.001",type:"number",value:(isNotNullOrUndefined(field_rx_state_?.["value"]) ? field_rx_state_?.["value"] : "")},),jsx(RadixThemesButton,{className:"icon-button",onClick:((_e) => (addEvents([(ReflexEvent("reflex___state____state.warframe_reflex___state____calculator_state.remove_damage_type", ({ ["group"] : "explosion_forced_proc", ["damage_name"] : field_rx_state_?.["name"] }), ({  })))], [_e], ({  })))),variant:"soft"},"\u00d7"))))))
  )
}


function Fragment_aa7ef3e02a6502918a5113a0a34db924 () {
  const reflex___state____state__warframe_reflex___state____calculator_state = useContext(StateContexts.reflex___state____state__warframe_reflex___state____calculator_state)



  return (
    jsx(Fragment,{},((reflex___state____state__warframe_reflex___state____calculator_state.explosion_forced_proc_fields_rx_state_.length > 0)?(jsx(Fragment,{},jsx(Flex_883b15394fa8cdd4dc0a40f86c041fe7,{},))):(jsx(Fragment,{},jsx(RadixThemesText,{as:"p",className:"empty-text"},"No damage types added.")))))
  )
}


function Fragment_632e7af2a3389a4718a8badaf069a49d () {
  const reflex___state____state__warframe_reflex___state____calculator_state = useContext(StateContexts.reflex___state____state__warframe_reflex___state____calculator_state)



  return (
    jsx(Fragment,{},(reflex___state____state__warframe_reflex___state____calculator_state.ranged_weapon_rx_state_?(jsx(Fragment,{},jsx(RadixThemesTabs.Root,{css:({ ["&[data-orientation='vertical']"] : ({ ["display"] : "flex" }), ["width"] : "100%" }),defaultValue:"direct"},jsx(RadixThemesTabs.List,{css:({ ["&[data-orientation='vertical']"] : ({ ["display"] : "block", ["boxShadow"] : "inset -1px 0 0 0 var(--gray-a5)" }) })},jsx(RadixThemesTabs.Trigger,{css:({ ["&[data-orientation='vertical']"] : ({ ["width"] : "100%" }) }),value:"direct"},"Direct Hit"),jsx(RadixThemesTabs.Trigger,{css:({ ["&[data-orientation='vertical']"] : ({ ["width"] : "100%" }) }),value:"explosion"},"Explosion")),jsx(RadixThemesTabs.Content,{css:({ ["&[data-orientation='vertical']"] : ({ ["width"] : "100%", ["margin"] : null }) }),value:"direct"},jsx(RadixThemesGrid,{className:"damage-editor-grid",columns:({ ["initial"] : "1", ["md"] : "2" }),css:({ ["gap"] : "0", ["width"] : "100%", ["paddingTop"] : "1rem" })},jsx(RadixThemesBox,{className:"subpanel"},jsx(RadixThemesFlex,{align:"start",className:"rx-Stack",css:({ ["gap"] : "3", ["width"] : "100%" }),direction:"column",gap:"3"},jsx(RadixThemesText,{as:"p",className:"card-title"},"Base Damage"),jsx(RadixThemesGrid,{columns:"minmax(0, 1fr) 32px",css:({ ["columnGap"] : "8px", ["width"] : "100%" })},jsx(Select__root_b34cfbe1c68a9b79f1867a236cb0f77b,{},),jsx(Button_268537da38ed2e5ba5c26342b7c13d89,{},)),jsx(Fragment_a7acf6cd05dce15c01ad7655ec9a7806,{},))),jsx(RadixThemesBox,{className:"subpanel"},jsx(RadixThemesFlex,{align:"start",className:"rx-Stack",css:({ ["gap"] : "3", ["width"] : "100%" }),direction:"column",gap:"3"},jsx(RadixThemesText,{as:"p",className:"card-title"},"Forced Procs"),jsx(RadixThemesGrid,{columns:"minmax(0, 1fr) 32px",css:({ ["columnGap"] : "8px", ["width"] : "100%" })},jsx(Select__root_a2bb3f1fafd729b0f88cf15ede2297e3,{},),jsx(Button_ad15771136b3037e79e2dca71cfb7b8a,{},)),jsx(Fragment_691cf2eb67157c3e06261e8d17c14f20,{},))))),jsx(RadixThemesTabs.Content,{css:({ ["&[data-orientation='vertical']"] : ({ ["width"] : "100%", ["margin"] : null }) }),value:"explosion"},jsx(RadixThemesGrid,{className:"damage-editor-grid",columns:({ ["initial"] : "1", ["md"] : "2" }),css:({ ["gap"] : "0", ["width"] : "100%", ["paddingTop"] : "1rem" })},jsx(RadixThemesBox,{className:"subpanel"},jsx(RadixThemesFlex,{align:"start",className:"rx-Stack",css:({ ["gap"] : "3", ["width"] : "100%" }),direction:"column",gap:"3"},jsx(RadixThemesText,{as:"p",className:"card-title"},"Explosion Damage"),jsx(RadixThemesGrid,{columns:"minmax(0, 1fr) 32px",css:({ ["columnGap"] : "8px", ["width"] : "100%" })},jsx(Select__root_99aeef4d268bca4723df429e37ea04fd,{},),jsx(Button_4bfb4b7408e884eba39534fcc0214214,{},)),jsx(Fragment_d812a4d7a33bcc63223181e7376c86cc,{},))),jsx(RadixThemesBox,{className:"subpanel"},jsx(RadixThemesFlex,{align:"start",className:"rx-Stack",css:({ ["gap"] : "3", ["width"] : "100%" }),direction:"column",gap:"3"},jsx(RadixThemesText,{as:"p",className:"card-title"},"Explosion Forced Procs"),jsx(RadixThemesGrid,{columns:"minmax(0, 1fr) 32px",css:({ ["columnGap"] : "8px", ["width"] : "100%" })},jsx(Select__root_89537645737e9323b096c1771d9f8cff,{},),jsx(Button_afbfa04c6516a8fb2be92ce58cb9d39a,{},)),jsx(Fragment_aa7ef3e02a6502918a5113a0a34db924,{},)))))))):(jsx(Fragment,{},jsx(RadixThemesGrid,{className:"damage-editor-grid",columns:({ ["initial"] : "1", ["md"] : "2" }),css:({ ["gap"] : "0", ["width"] : "100%" })},jsx(RadixThemesBox,{className:"subpanel"},jsx(RadixThemesFlex,{align:"start",className:"rx-Stack",css:({ ["gap"] : "3", ["width"] : "100%" }),direction:"column",gap:"3"},jsx(RadixThemesText,{as:"p",className:"card-title"},"Light Attack Damage"),jsx(RadixThemesGrid,{columns:"minmax(0, 1fr) 32px",css:({ ["columnGap"] : "8px", ["width"] : "100%" })},jsx(Select__root_b34cfbe1c68a9b79f1867a236cb0f77b,{},),jsx(Button_268537da38ed2e5ba5c26342b7c13d89,{},)),jsx(Fragment_a7acf6cd05dce15c01ad7655ec9a7806,{},))),jsx(RadixThemesBox,{className:"subpanel"},jsx(RadixThemesFlex,{align:"start",className:"rx-Stack",css:({ ["gap"] : "3", ["width"] : "100%" }),direction:"column",gap:"3"},jsx(RadixThemesText,{as:"p",className:"card-title"},"Light Attack Forced Procs"),jsx(RadixThemesGrid,{columns:"minmax(0, 1fr) 32px",css:({ ["columnGap"] : "8px", ["width"] : "100%" })},jsx(Select__root_a2bb3f1fafd729b0f88cf15ede2297e3,{},),jsx(Button_ad15771136b3037e79e2dca71cfb7b8a,{},)),jsx(Fragment_691cf2eb67157c3e06261e8d17c14f20,{},))))))))
  )
}


function Select__root_a6f9ba94cbbc5cf01dc19f7826abc42e () {
  const reflex___state____state__warframe_reflex___state____calculator_state = useContext(StateContexts.reflex___state____state__warframe_reflex___state____calculator_state)
const [addEvents, connectErrors] = useContext(EventLoopContext);

const on_change_88b2f29dce412fa8c7b4bfb8c9c64456 = useCallback(((_ev_0) => (addEvents([(ReflexEvent("reflex___state____state.warframe_reflex___state____calculator_state.set_progenitor_element", ({ ["value"] : _ev_0 }), ({  })))], [_ev_0], ({  })))), [addEvents, ReflexEvent])

  return (
    jsx(RadixThemesSelect.Root,{disabled:false,onValueChange:on_change_88b2f29dce412fa8c7b4bfb8c9c64456,value:reflex___state____state__warframe_reflex___state____calculator_state.progenitor_element_rx_state_},jsx(RadixThemesSelect.Trigger,{css:({ ["width"] : "100%" })},),jsx(RadixThemesSelect.Content,{position:"popper"},jsx(RadixThemesSelect.Group,{},"",jsx(RadixThemesSelect.Item,{value:"None"},"None"),jsx(RadixThemesSelect.Item,{value:"impact"},"impact"),jsx(RadixThemesSelect.Item,{value:"cold"},"cold"),jsx(RadixThemesSelect.Item,{value:"electricity"},"electricity"),jsx(RadixThemesSelect.Item,{value:"heat"},"heat"),jsx(RadixThemesSelect.Item,{value:"toxin"},"toxin"),jsx(RadixThemesSelect.Item,{value:"magnetic"},"magnetic"),jsx(RadixThemesSelect.Item,{value:"radiation"},"radiation"))))
  )
}


function Debounceinput_cdd776c32eacd24c46da47f484d0267b () {
  const reflex___state____state__warframe_reflex___state____calculator_state = useContext(StateContexts.reflex___state____state__warframe_reflex___state____calculator_state)
const [addEvents, connectErrors] = useContext(EventLoopContext);

const on_change_85d4106400bb088a99493d93ff37c5b6 = useCallback(((_e) => (addEvents([(ReflexEvent("reflex___state____state.warframe_reflex___state____calculator_state.set_base_number", ({ ["field_name"] : "progenitor_value", ["value"] : _e?.["target"]?.["value"] }), ({  })))], [_e], ({  })))), [addEvents, ReflexEvent])

  return (
    jsx(DebounceInput,{css:({ ["width"] : "100%", ["debounceTimeout"] : 250 }),debounceTimeout:250,element:RadixThemesTextField.Root,max:10,min:0,onChange:on_change_85d4106400bb088a99493d93ff37c5b6,step:"0.001",type:"number",value:(isNotNullOrUndefined(reflex___state____state__warframe_reflex___state____calculator_state.progenitor_value_rx_state_) ? reflex___state____state__warframe_reflex___state____calculator_state.progenitor_value_rx_state_ : "")},)
  )
}


function Debounceinput_7aa54a834190be12b87e94dfb9a77122 () {
  const reflex___state____state__warframe_reflex___state____calculator_state = useContext(StateContexts.reflex___state____state__warframe_reflex___state____calculator_state)
const [addEvents, connectErrors] = useContext(EventLoopContext);

const on_change_94b9c9a0b48c27a565567204af381485 = useCallback(((_e) => (addEvents([(ReflexEvent("reflex___state____state.warframe_reflex___state____calculator_state.set_base_number", ({ ["field_name"] : "base_crit_chance", ["value"] : _e?.["target"]?.["value"] }), ({  })))], [_e], ({  })))), [addEvents, ReflexEvent])

  return (
    jsx(DebounceInput,{css:({ ["width"] : "100%", ["debounceTimeout"] : 250 }),debounceTimeout:250,element:RadixThemesTextField.Root,max:10,min:0,onChange:on_change_94b9c9a0b48c27a565567204af381485,step:"0.001",type:"number",value:(isNotNullOrUndefined(reflex___state____state__warframe_reflex___state____calculator_state.base_crit_chance_rx_state_) ? reflex___state____state__warframe_reflex___state____calculator_state.base_crit_chance_rx_state_ : "")},)
  )
}


function Debounceinput_970c1bbc942a13ecd299d7f5c06b8bd2 () {
  const reflex___state____state__warframe_reflex___state____calculator_state = useContext(StateContexts.reflex___state____state__warframe_reflex___state____calculator_state)
const [addEvents, connectErrors] = useContext(EventLoopContext);

const on_change_6a9319da6fc1b048d32786607991aea6 = useCallback(((_e) => (addEvents([(ReflexEvent("reflex___state____state.warframe_reflex___state____calculator_state.set_base_number", ({ ["field_name"] : "base_crit_damage", ["value"] : _e?.["target"]?.["value"] }), ({  })))], [_e], ({  })))), [addEvents, ReflexEvent])

  return (
    jsx(DebounceInput,{css:({ ["width"] : "100%", ["debounceTimeout"] : 250 }),debounceTimeout:250,element:RadixThemesTextField.Root,max:20,min:1,onChange:on_change_6a9319da6fc1b048d32786607991aea6,step:"0.001",type:"number",value:(isNotNullOrUndefined(reflex___state____state__warframe_reflex___state____calculator_state.base_crit_damage_rx_state_) ? reflex___state____state__warframe_reflex___state____calculator_state.base_crit_damage_rx_state_ : "")},)
  )
}


function Debounceinput_34794b3dd402f7139860ebe3c6c4ce2d () {
  const reflex___state____state__warframe_reflex___state____calculator_state = useContext(StateContexts.reflex___state____state__warframe_reflex___state____calculator_state)
const [addEvents, connectErrors] = useContext(EventLoopContext);

const on_change_285b10d789ee12ac8ccc99fe98714a2f = useCallback(((_e) => (addEvents([(ReflexEvent("reflex___state____state.warframe_reflex___state____calculator_state.set_base_number", ({ ["field_name"] : "base_status_chance", ["value"] : _e?.["target"]?.["value"] }), ({  })))], [_e], ({  })))), [addEvents, ReflexEvent])

  return (
    jsx(DebounceInput,{css:({ ["width"] : "100%", ["debounceTimeout"] : 250 }),debounceTimeout:250,element:RadixThemesTextField.Root,max:10,min:0,onChange:on_change_285b10d789ee12ac8ccc99fe98714a2f,step:"0.001",type:"number",value:(isNotNullOrUndefined(reflex___state____state__warframe_reflex___state____calculator_state.base_status_chance_rx_state_) ? reflex___state____state__warframe_reflex___state____calculator_state.base_status_chance_rx_state_ : "")},)
  )
}


function Debounceinput_a70e4053a0dbd5ece114dca4ed12ef00 () {
  const reflex___state____state__warframe_reflex___state____calculator_state = useContext(StateContexts.reflex___state____state__warframe_reflex___state____calculator_state)
const [addEvents, connectErrors] = useContext(EventLoopContext);

const on_change_e416b6f8f465923dad0d135e05dd33d5 = useCallback(((_e) => (addEvents([(ReflexEvent("reflex___state____state.warframe_reflex___state____calculator_state.set_base_number", ({ ["field_name"] : "base_multishot", ["value"] : _e?.["target"]?.["value"] }), ({  })))], [_e], ({  })))), [addEvents, ReflexEvent])

  return (
    jsx(DebounceInput,{css:({ ["width"] : "100%", ["debounceTimeout"] : 250 }),debounceTimeout:250,element:RadixThemesTextField.Root,max:100,min:1,onChange:on_change_e416b6f8f465923dad0d135e05dd33d5,step:"0.001",type:"number",value:(isNotNullOrUndefined(reflex___state____state__warframe_reflex___state____calculator_state.base_multishot_rx_state_) ? reflex___state____state__warframe_reflex___state____calculator_state.base_multishot_rx_state_ : "")},)
  )
}


function Debounceinput_2c5756be2da30da58f73e4d93e6cd64e () {
  const reflex___state____state__warframe_reflex___state____calculator_state = useContext(StateContexts.reflex___state____state__warframe_reflex___state____calculator_state)
const [addEvents, connectErrors] = useContext(EventLoopContext);

const on_change_89a958c0a49e79b281261b6ccc6f9527 = useCallback(((_e) => (addEvents([(ReflexEvent("reflex___state____state.warframe_reflex___state____calculator_state.set_base_number", ({ ["field_name"] : "base_fire_rate", ["value"] : _e?.["target"]?.["value"] }), ({  })))], [_e], ({  })))), [addEvents, ReflexEvent])

  return (
    jsx(DebounceInput,{css:({ ["width"] : "100%", ["debounceTimeout"] : 250 }),debounceTimeout:250,element:RadixThemesTextField.Root,max:100,min:0.05,onChange:on_change_89a958c0a49e79b281261b6ccc6f9527,step:"0.001",type:"number",value:(isNotNullOrUndefined(reflex___state____state__warframe_reflex___state____calculator_state.base_fire_rate_rx_state_) ? reflex___state____state__warframe_reflex___state____calculator_state.base_fire_rate_rx_state_ : "")},)
  )
}


function Debounceinput_ed9565a59be998ca24361401f0f978ca () {
  const reflex___state____state__warframe_reflex___state____calculator_state = useContext(StateContexts.reflex___state____state__warframe_reflex___state____calculator_state)
const [addEvents, connectErrors] = useContext(EventLoopContext);

const on_change_87279097c88ef19448bd5fbd7783f865 = useCallback(((_e) => (addEvents([(ReflexEvent("reflex___state____state.warframe_reflex___state____calculator_state.set_base_number", ({ ["field_name"] : "base_reload_speed", ["value"] : _e?.["target"]?.["value"] }), ({  })))], [_e], ({  })))), [addEvents, ReflexEvent])

  return (
    jsx(DebounceInput,{css:({ ["width"] : "100%", ["debounceTimeout"] : 250 }),debounceTimeout:250,element:RadixThemesTextField.Root,max:20,min:0,onChange:on_change_87279097c88ef19448bd5fbd7783f865,step:"0.001",type:"number",value:(isNotNullOrUndefined(reflex___state____state__warframe_reflex___state____calculator_state.base_reload_speed_rx_state_) ? reflex___state____state__warframe_reflex___state____calculator_state.base_reload_speed_rx_state_ : "")},)
  )
}


function Debounceinput_be7dd8992b36ddc508e67c268d46b2be () {
  const reflex___state____state__warframe_reflex___state____calculator_state = useContext(StateContexts.reflex___state____state__warframe_reflex___state____calculator_state)
const [addEvents, connectErrors] = useContext(EventLoopContext);

const on_change_66c0cfb7f5215865a9757b2dc8d67b9c = useCallback(((_e) => (addEvents([(ReflexEvent("reflex___state____state.warframe_reflex___state____calculator_state.set_base_number", ({ ["field_name"] : "base_magazine_capacity", ["value"] : _e?.["target"]?.["value"] }), ({  })))], [_e], ({  })))), [addEvents, ReflexEvent])

  return (
    jsx(DebounceInput,{css:({ ["width"] : "100%", ["debounceTimeout"] : 250 }),debounceTimeout:250,element:RadixThemesTextField.Root,max:10000,min:1,onChange:on_change_66c0cfb7f5215865a9757b2dc8d67b9c,step:"1",type:"number",value:(isNotNullOrUndefined(reflex___state____state__warframe_reflex___state____calculator_state.base_magazine_capacity_rx_state_) ? reflex___state____state__warframe_reflex___state____calculator_state.base_magazine_capacity_rx_state_ : "")},)
  )
}


function Debounceinput_7cab1ddc3b8ebec06b60bf81097d2717 () {
  const reflex___state____state__warframe_reflex___state____calculator_state = useContext(StateContexts.reflex___state____state__warframe_reflex___state____calculator_state)
const [addEvents, connectErrors] = useContext(EventLoopContext);

const on_change_e45cbf48f21477648c7633cd9af088aa = useCallback(((_e) => (addEvents([(ReflexEvent("reflex___state____state.warframe_reflex___state____calculator_state.set_base_number", ({ ["field_name"] : "base_weakpoint_damage", ["value"] : _e?.["target"]?.["value"] }), ({  })))], [_e], ({  })))), [addEvents, ReflexEvent])

  return (
    jsx(DebounceInput,{css:({ ["width"] : "100%", ["debounceTimeout"] : 250 }),debounceTimeout:250,element:RadixThemesTextField.Root,max:20,min:1,onChange:on_change_e45cbf48f21477648c7633cd9af088aa,step:"0.001",type:"number",value:(isNotNullOrUndefined(reflex___state____state__warframe_reflex___state____calculator_state.base_weakpoint_damage_rx_state_) ? reflex___state____state__warframe_reflex___state____calculator_state.base_weakpoint_damage_rx_state_ : "")},)
  )
}


function Debounceinput_fc204b8c0bae3c21a665e753f70e17f6 () {
  const reflex___state____state__warframe_reflex___state____calculator_state = useContext(StateContexts.reflex___state____state__warframe_reflex___state____calculator_state)
const [addEvents, connectErrors] = useContext(EventLoopContext);

const on_change_2dd7ecde500df1f2e53a5b03513395c8 = useCallback(((_e) => (addEvents([(ReflexEvent("reflex___state____state.warframe_reflex___state____calculator_state.set_base_number", ({ ["field_name"] : "base_recharge_rate", ["value"] : _e?.["target"]?.["value"] }), ({  })))], [_e], ({  })))), [addEvents, ReflexEvent])

  return (
    jsx(DebounceInput,{css:({ ["width"] : "100%", ["debounceTimeout"] : 250 }),debounceTimeout:250,element:RadixThemesTextField.Root,max:1000,min:0,onChange:on_change_2dd7ecde500df1f2e53a5b03513395c8,step:"0.001",type:"number",value:(isNotNullOrUndefined(reflex___state____state__warframe_reflex___state____calculator_state.base_recharge_rate_rx_state_) ? reflex___state____state__warframe_reflex___state____calculator_state.base_recharge_rate_rx_state_ : "")},)
  )
}


function Fragment_1a53689b1fbfba90380765d88e957aff () {
  const reflex___state____state__warframe_reflex___state____calculator_state = useContext(StateContexts.reflex___state____state__warframe_reflex___state____calculator_state)



  return (
    jsx(Fragment,{},(reflex___state____state__warframe_reflex___state____calculator_state.is_battery_rx_state_?(jsx(Fragment,{},jsx(RadixThemesFlex,{align:"start",className:"rx-Stack",css:({ ["gap"] : "1", ["width"] : "100%" }),direction:"column",gap:"3"},jsx(RadixThemesText,{as:"p",className:"field-label"},"Recharge Rate"),jsx(Debounceinput_fc204b8c0bae3c21a665e753f70e17f6,{},)))):(jsx(Fragment,{},))))
  )
}


function Debounceinput_054ff5c57090cfa713ce62944b42a4f3 () {
  const reflex___state____state__warframe_reflex___state____calculator_state = useContext(StateContexts.reflex___state____state__warframe_reflex___state____calculator_state)
const [addEvents, connectErrors] = useContext(EventLoopContext);

const on_change_8099462398292f4386cd8b9b8e531bc0 = useCallback(((_e) => (addEvents([(ReflexEvent("reflex___state____state.warframe_reflex___state____calculator_state.set_base_number", ({ ["field_name"] : "base_charge_time", ["value"] : _e?.["target"]?.["value"] }), ({  })))], [_e], ({  })))), [addEvents, ReflexEvent])

  return (
    jsx(DebounceInput,{css:({ ["width"] : "100%", ["debounceTimeout"] : 250 }),debounceTimeout:250,element:RadixThemesTextField.Root,max:20,min:0,onChange:on_change_8099462398292f4386cd8b9b8e531bc0,step:"0.001",type:"number",value:(isNotNullOrUndefined(reflex___state____state__warframe_reflex___state____calculator_state.base_charge_time_rx_state_) ? reflex___state____state__warframe_reflex___state____calculator_state.base_charge_time_rx_state_ : "")},)
  )
}


function Fragment_120b0db12b36713aea9af61e1c24c2a0 () {
  const reflex___state____state__warframe_reflex___state____calculator_state = useContext(StateContexts.reflex___state____state__warframe_reflex___state____calculator_state)



  return (
    jsx(Fragment,{},(reflex___state____state__warframe_reflex___state____calculator_state.is_charge_weapon_rx_state_?(jsx(Fragment,{},jsx(RadixThemesFlex,{align:"start",className:"rx-Stack",css:({ ["gap"] : "1", ["width"] : "100%" }),direction:"column",gap:"3"},jsx(RadixThemesText,{as:"p",className:"field-label"},"Charge Time"),jsx(Debounceinput_054ff5c57090cfa713ce62944b42a4f3,{},)))):(jsx(Fragment,{},))))
  )
}


function Debounceinput_a9a1060008b60409d9b50586f3b47461 () {
  const reflex___state____state__warframe_reflex___state____calculator_state = useContext(StateContexts.reflex___state____state__warframe_reflex___state____calculator_state)
const [addEvents, connectErrors] = useContext(EventLoopContext);

const on_change_b0222b18ebffed1563572e8f50a3902c = useCallback(((_e) => (addEvents([(ReflexEvent("reflex___state____state.warframe_reflex___state____calculator_state.set_base_number", ({ ["field_name"] : "base_burst_count", ["value"] : _e?.["target"]?.["value"] }), ({  })))], [_e], ({  })))), [addEvents, ReflexEvent])

  return (
    jsx(DebounceInput,{css:({ ["width"] : "100%", ["debounceTimeout"] : 250 }),debounceTimeout:250,element:RadixThemesTextField.Root,max:100,min:1,onChange:on_change_b0222b18ebffed1563572e8f50a3902c,step:"1",type:"number",value:(isNotNullOrUndefined(reflex___state____state__warframe_reflex___state____calculator_state.base_burst_count_rx_state_) ? reflex___state____state__warframe_reflex___state____calculator_state.base_burst_count_rx_state_ : "")},)
  )
}


function Fragment_7bce9930884c7c2f2eb65b3554c8a64a () {
  const reflex___state____state__warframe_reflex___state____calculator_state = useContext(StateContexts.reflex___state____state__warframe_reflex___state____calculator_state)



  return (
    jsx(Fragment,{},(reflex___state____state__warframe_reflex___state____calculator_state.is_burst_weapon_rx_state_?(jsx(Fragment,{},jsx(RadixThemesFlex,{align:"start",className:"rx-Stack",css:({ ["gap"] : "1", ["width"] : "100%" }),direction:"column",gap:"3"},jsx(RadixThemesText,{as:"p",className:"field-label"},"Burst Count"),jsx(Debounceinput_a9a1060008b60409d9b50586f3b47461,{},)))):(jsx(Fragment,{},))))
  )
}


function Debounceinput_18042c19e64e25ffb415716625c16f6f () {
  const reflex___state____state__warframe_reflex___state____calculator_state = useContext(StateContexts.reflex___state____state__warframe_reflex___state____calculator_state)
const [addEvents, connectErrors] = useContext(EventLoopContext);

const on_change_96c3cc834123fe4dd95cc989181704c0 = useCallback(((_e) => (addEvents([(ReflexEvent("reflex___state____state.warframe_reflex___state____calculator_state.set_base_number", ({ ["field_name"] : "base_burst_delay", ["value"] : _e?.["target"]?.["value"] }), ({  })))], [_e], ({  })))), [addEvents, ReflexEvent])

  return (
    jsx(DebounceInput,{css:({ ["width"] : "100%", ["debounceTimeout"] : 250 }),debounceTimeout:250,element:RadixThemesTextField.Root,max:20,min:0,onChange:on_change_96c3cc834123fe4dd95cc989181704c0,step:"0.001",type:"number",value:(isNotNullOrUndefined(reflex___state____state__warframe_reflex___state____calculator_state.base_burst_delay_rx_state_) ? reflex___state____state__warframe_reflex___state____calculator_state.base_burst_delay_rx_state_ : "")},)
  )
}


function Fragment_f1554a457137da74e8580ee5a1eedab3 () {
  const reflex___state____state__warframe_reflex___state____calculator_state = useContext(StateContexts.reflex___state____state__warframe_reflex___state____calculator_state)



  return (
    jsx(Fragment,{},(reflex___state____state__warframe_reflex___state____calculator_state.is_burst_weapon_rx_state_?(jsx(Fragment,{},jsx(RadixThemesFlex,{align:"start",className:"rx-Stack",css:({ ["gap"] : "1", ["width"] : "100%" }),direction:"column",gap:"3"},jsx(RadixThemesText,{as:"p",className:"field-label"},"Burst Delay"),jsx(Debounceinput_18042c19e64e25ffb415716625c16f6f,{},)))):(jsx(Fragment,{},))))
  )
}


function Debounceinput_7a7dec570683ba01a595126c9fc3a6b7 () {
  const reflex___state____state__warframe_reflex___state____calculator_state = useContext(StateContexts.reflex___state____state__warframe_reflex___state____calculator_state)
const [addEvents, connectErrors] = useContext(EventLoopContext);

const on_change_422e5847b5b61041cc72fe587e7dd7c2 = useCallback(((_e) => (addEvents([(ReflexEvent("reflex___state____state.warframe_reflex___state____calculator_state.set_base_number", ({ ["field_name"] : "base_attack_speed", ["value"] : _e?.["target"]?.["value"] }), ({  })))], [_e], ({  })))), [addEvents, ReflexEvent])

  return (
    jsx(DebounceInput,{css:({ ["width"] : "100%", ["debounceTimeout"] : 250 }),debounceTimeout:250,element:RadixThemesTextField.Root,max:20,min:0,onChange:on_change_422e5847b5b61041cc72fe587e7dd7c2,step:"0.001",type:"number",value:(isNotNullOrUndefined(reflex___state____state__warframe_reflex___state____calculator_state.base_attack_speed_rx_state_) ? reflex___state____state__warframe_reflex___state____calculator_state.base_attack_speed_rx_state_ : "")},)
  )
}


function Fragment_1384174ab64122d377ae45447cb19055 () {
  const reflex___state____state__warframe_reflex___state____calculator_state = useContext(StateContexts.reflex___state____state__warframe_reflex___state____calculator_state)



  return (
    jsx(Fragment,{},(reflex___state____state__warframe_reflex___state____calculator_state.ranged_weapon_rx_state_?(jsx(Fragment,{},jsx(RadixThemesFlex,{align:"start",className:"rx-Stack control-row-stack",css:({ ["width"] : "100%", ["gap"] : "2" }),direction:"column",gap:"3"},jsx(RadixThemesGrid,{className:"form-grid form-grid-4",columns:({ ["initial"] : "1", ["sm"] : "2", ["lg"] : "4" }),css:({ ["gap"] : "4", ["width"] : "100%" })},jsx(RadixThemesFlex,{align:"start",className:"rx-Stack",css:({ ["gap"] : "1", ["width"] : "100%" }),direction:"column",gap:"3"},jsx(RadixThemesText,{as:"p",className:"field-label"},"Crit Chance"),jsx(Debounceinput_7aa54a834190be12b87e94dfb9a77122,{},)),jsx(RadixThemesFlex,{align:"start",className:"rx-Stack",css:({ ["gap"] : "1", ["width"] : "100%" }),direction:"column",gap:"3"},jsx(RadixThemesText,{as:"p",className:"field-label"},"Crit Damage"),jsx(Debounceinput_970c1bbc942a13ecd299d7f5c06b8bd2,{},)),jsx(RadixThemesFlex,{align:"start",className:"rx-Stack",css:({ ["gap"] : "1", ["width"] : "100%" }),direction:"column",gap:"3"},jsx(RadixThemesText,{as:"p",className:"field-label"},"Status Chance"),jsx(Debounceinput_34794b3dd402f7139860ebe3c6c4ce2d,{},)),jsx(RadixThemesFlex,{align:"start",className:"rx-Stack",css:({ ["gap"] : "1", ["width"] : "100%" }),direction:"column",gap:"3"},jsx(RadixThemesText,{as:"p",className:"field-label"},"Multishot"),jsx(Debounceinput_a70e4053a0dbd5ece114dca4ed12ef00,{},))),jsx(RadixThemesGrid,{className:"form-grid form-grid-4",columns:({ ["initial"] : "1", ["sm"] : "2", ["lg"] : "4" }),css:({ ["gap"] : "4", ["width"] : "100%" })},jsx(RadixThemesFlex,{align:"start",className:"rx-Stack",css:({ ["gap"] : "1", ["width"] : "100%" }),direction:"column",gap:"3"},jsx(RadixThemesText,{as:"p",className:"field-label"},"Fire Rate"),jsx(Debounceinput_2c5756be2da30da58f73e4d93e6cd64e,{},)),jsx(RadixThemesFlex,{align:"start",className:"rx-Stack",css:({ ["gap"] : "1", ["width"] : "100%" }),direction:"column",gap:"3"},jsx(RadixThemesText,{as:"p",className:"field-label"},"Reload Speed"),jsx(Debounceinput_ed9565a59be998ca24361401f0f978ca,{},)),jsx(RadixThemesFlex,{align:"start",className:"rx-Stack",css:({ ["gap"] : "1", ["width"] : "100%" }),direction:"column",gap:"3"},jsx(RadixThemesText,{as:"p",className:"field-label"},"Magazine Capacity"),jsx(Debounceinput_be7dd8992b36ddc508e67c268d46b2be,{},)),jsx(RadixThemesFlex,{align:"start",className:"rx-Stack",css:({ ["gap"] : "1", ["width"] : "100%" }),direction:"column",gap:"3"},jsx(RadixThemesText,{as:"p",className:"field-label"},"Weakpoint Damage"),jsx(Debounceinput_7cab1ddc3b8ebec06b60bf81097d2717,{},))),jsx(RadixThemesGrid,{className:"form-grid form-grid-4",columns:({ ["initial"] : "1", ["sm"] : "2", ["lg"] : "4" }),css:({ ["gap"] : "4", ["width"] : "100%" })},jsx(Fragment_1a53689b1fbfba90380765d88e957aff,{},),jsx(Fragment_120b0db12b36713aea9af61e1c24c2a0,{},),jsx(Fragment_7bce9930884c7c2f2eb65b3554c8a64a,{},),jsx(Fragment_f1554a457137da74e8580ee5a1eedab3,{},))))):(jsx(Fragment,{},jsx(RadixThemesGrid,{className:"form-grid form-grid-4",columns:({ ["initial"] : "1", ["sm"] : "2", ["lg"] : "4" }),css:({ ["gap"] : "4", ["width"] : "100%" })},jsx(RadixThemesFlex,{align:"start",className:"rx-Stack",css:({ ["gap"] : "1", ["width"] : "100%" }),direction:"column",gap:"3"},jsx(RadixThemesText,{as:"p",className:"field-label"},"Crit Chance"),jsx(Debounceinput_7aa54a834190be12b87e94dfb9a77122,{},)),jsx(RadixThemesFlex,{align:"start",className:"rx-Stack",css:({ ["gap"] : "1", ["width"] : "100%" }),direction:"column",gap:"3"},jsx(RadixThemesText,{as:"p",className:"field-label"},"Crit Damage"),jsx(Debounceinput_970c1bbc942a13ecd299d7f5c06b8bd2,{},)),jsx(RadixThemesFlex,{align:"start",className:"rx-Stack",css:({ ["gap"] : "1", ["width"] : "100%" }),direction:"column",gap:"3"},jsx(RadixThemesText,{as:"p",className:"field-label"},"Status Chance"),jsx(Debounceinput_34794b3dd402f7139860ebe3c6c4ce2d,{},)),jsx(RadixThemesFlex,{align:"start",className:"rx-Stack",css:({ ["gap"] : "1", ["width"] : "100%" }),direction:"column",gap:"3"},jsx(RadixThemesText,{as:"p",className:"field-label"},"Attack Speed"),jsx(Debounceinput_7a7dec570683ba01a595126c9fc3a6b7,{},)))))))
  )
}


function Fragment_44436c3c26f609346484b43b31c366bb () {
  const reflex___state____state__warframe_reflex___state____calculator_state = useContext(StateContexts.reflex___state____state__warframe_reflex___state____calculator_state)



  return (
    jsx(Fragment,{},(reflex___state____state__warframe_reflex___state____calculator_state.custom_weapon_rx_state_?(jsx(Fragment,{},jsx(RadixThemesFlex,{align:"start",className:"rx-Stack",css:({ ["width"] : "100%", ["gap"] : "5" }),direction:"column",gap:"3"},jsx(Fragment_af1ebccbd20d0f03f339f2b75d67b3ff,{},),jsx(Fragment_632e7af2a3389a4718a8badaf069a49d,{},),jsx(RadixThemesGrid,{className:"form-grid form-grid-2",columns:({ ["initial"] : "1", ["sm"] : "2" }),css:({ ["gap"] : "4", ["width"] : "100%" })},jsx(RadixThemesFlex,{align:"start",className:"rx-Stack",css:({ ["gap"] : "1", ["width"] : "100%" }),direction:"column",gap:"3"},jsx(RadixThemesText,{as:"p",className:"field-label"},"Progenitor Element"),jsx(Select__root_a6f9ba94cbbc5cf01dc19f7826abc42e,{},)),jsx(RadixThemesFlex,{align:"start",className:"rx-Stack",css:({ ["gap"] : "1", ["width"] : "100%" }),direction:"column",gap:"3"},jsx(RadixThemesText,{as:"p",className:"field-label"},"Progenitor Value"),jsx(Debounceinput_cdd776c32eacd24c46da47f484d0267b,{},))),jsx(Fragment_1384174ab64122d377ae45447cb19055,{},)))):(jsx(Fragment,{},jsx(RadixThemesGrid,{className:"form-grid form-grid-2",columns:({ ["initial"] : "1", ["sm"] : "2" }),css:({ ["gap"] : "4", ["width"] : "100%" })},jsx(RadixThemesFlex,{align:"start",className:"rx-Stack",css:({ ["gap"] : "1", ["width"] : "100%" }),direction:"column",gap:"3"},jsx(RadixThemesText,{as:"p",className:"field-label"},"Progenitor Element"),jsx(Select__root_a6f9ba94cbbc5cf01dc19f7826abc42e,{},)),jsx(RadixThemesFlex,{align:"start",className:"rx-Stack",css:({ ["gap"] : "1", ["width"] : "100%" }),direction:"column",gap:"3"},jsx(RadixThemesText,{as:"p",className:"field-label"},"Progenitor Value"),jsx(Debounceinput_cdd776c32eacd24c46da47f484d0267b,{},)))))))
  )
}


function Badge_e5892c5677fa1c50a593e45b62fa0c27 () {
  const reflex___state____state__warframe_reflex___state____calculator_state = useContext(StateContexts.reflex___state____state__warframe_reflex___state____calculator_state)



  return (
    jsx(RadixThemesBadge,{className:"contribution-badge",variant:"soft"},reflex___state____state__warframe_reflex___state____calculator_state.slot_contributions_rx_state_?.at?.(0))
  )
}


function Select__group_a3ecac2495351b434ca1713de89fa7a8 () {
  const reflex___state____state__warframe_reflex___state____calculator_state = useContext(StateContexts.reflex___state____state__warframe_reflex___state____calculator_state)



  return (
    jsx(RadixThemesSelect.Group,{},"",Array.prototype.map.call(reflex___state____state__warframe_reflex___state____calculator_state.mod_options_rx_state_ ?? [],((item_rx_state_,index_d6d6157c99650830f12a866606ea87b7)=>(jsx(RadixThemesSelect.Item,{key:index_d6d6157c99650830f12a866606ea87b7,value:item_rx_state_},item_rx_state_)))))
  )
}


function Select__root_bc8fbbbfa613543ced82d007de8c255a () {
  const reflex___state____state__warframe_reflex___state____calculator_state = useContext(StateContexts.reflex___state____state__warframe_reflex___state____calculator_state)
const [addEvents, connectErrors] = useContext(EventLoopContext);

const on_change_4a1c051961b2841038fb6b3b62d4b7bd = useCallback(((_ev_0) => (addEvents([(ReflexEvent("reflex___state____state.warframe_reflex___state____calculator_state.set_slot_upgrade", ({ ["index"] : 0, ["value"] : _ev_0 }), ({  })))], [_ev_0], ({  })))), [addEvents, ReflexEvent])

  return (
    jsx(RadixThemesSelect.Root,{onValueChange:on_change_4a1c051961b2841038fb6b3b62d4b7bd,value:reflex___state____state__warframe_reflex___state____calculator_state.slot_selected_upgrades_rx_state_?.at?.(0)},jsx(RadixThemesSelect.Trigger,{css:({ ["width"] : "100%" })},),jsx(RadixThemesSelect.Content,{position:"popper"},jsx(Select__group_a3ecac2495351b434ca1713de89fa7a8,{},)))
  )
}


function Debounceinput_3ce27737ae615357d63b32a9d04184a8 () {
  const reflex___state____state__warframe_reflex___state____calculator_state = useContext(StateContexts.reflex___state____state__warframe_reflex___state____calculator_state)
const [addEvents, connectErrors] = useContext(EventLoopContext);

const on_change_aa2770335708a98878eb03dba094185f = useCallback(((_e) => (addEvents([(ReflexEvent("reflex___state____state.warframe_reflex___state____calculator_state.set_slot_rank", ({ ["index"] : 0, ["value"] : _e?.["target"]?.["value"] }), ({  })))], [_e], ({  })))), [addEvents, ReflexEvent])

  return (
    jsx(DebounceInput,{css:({ ["width"] : "100%", ["debounceTimeout"] : 250 }),debounceTimeout:250,element:RadixThemesTextField.Root,max:reflex___state____state__warframe_reflex___state____calculator_state.slot_max_ranks_rx_state_?.at?.(0),min:0,onChange:on_change_aa2770335708a98878eb03dba094185f,step:"1",type:"number",value:(isNotNullOrUndefined(reflex___state____state__warframe_reflex___state____calculator_state.slot_ranks_rx_state_?.at?.(0)) ? reflex___state____state__warframe_reflex___state____calculator_state.slot_ranks_rx_state_?.at?.(0) : "")},)
  )
}


function Debounceinput_08da6b9ec37d732d0016aea89c49eb97 () {
  const reflex___state____state__warframe_reflex___state____calculator_state = useContext(StateContexts.reflex___state____state__warframe_reflex___state____calculator_state)
const [addEvents, connectErrors] = useContext(EventLoopContext);

const on_change_d381de80ba560cf014dacb84186b464d = useCallback(((_e) => (addEvents([(ReflexEvent("reflex___state____state.warframe_reflex___state____calculator_state.set_slot_stacks", ({ ["index"] : 0, ["value"] : _e?.["target"]?.["value"] }), ({  })))], [_e], ({  })))), [addEvents, ReflexEvent])

  return (
    jsx(DebounceInput,{css:({ ["width"] : "100%", ["debounceTimeout"] : 250 }),debounceTimeout:250,element:RadixThemesTextField.Root,max:reflex___state____state__warframe_reflex___state____calculator_state.slot_max_stacks_rx_state_?.at?.(0),min:0,onChange:on_change_d381de80ba560cf014dacb84186b464d,step:"1",type:"number",value:(isNotNullOrUndefined(reflex___state____state__warframe_reflex___state____calculator_state.slot_stacks_rx_state_?.at?.(0)) ? reflex___state____state__warframe_reflex___state____calculator_state.slot_stacks_rx_state_?.at?.(0) : "")},)
  )
}


function Fragment_8342be9ccfb17533524924e8b3c51d19 () {
  const reflex___state____state__warframe_reflex___state____calculator_state = useContext(StateContexts.reflex___state____state__warframe_reflex___state____calculator_state)



  return (
    jsx(Fragment,{},((reflex___state____state__warframe_reflex___state____calculator_state.slot_max_stacks_rx_state_?.at?.(0) > 0)?(jsx(Fragment,{},jsx(RadixThemesFlex,{align:"start",className:"rx-Stack",css:({ ["gap"] : "1", ["width"] : "100%" }),direction:"column",gap:"3"},jsx(RadixThemesText,{as:"p",className:"field-label"},"Stacks"),jsx(Debounceinput_08da6b9ec37d732d0016aea89c49eb97,{},)))):(jsx(Fragment,{},))))
  )
}


function Checkbox_1c9ce19dbbeeac9c110d1988207260dd () {
  const reflex___state____state__warframe_reflex___state____calculator_state = useContext(StateContexts.reflex___state____state__warframe_reflex___state____calculator_state)
const [addEvents, connectErrors] = useContext(EventLoopContext);

const on_change_6730515b99e8e4e3ead73c5362eb824c = useCallback(((_ev_0) => (addEvents([(ReflexEvent("reflex___state____state.warframe_reflex___state____calculator_state.set_slot_condition", ({ ["index"] : 0, ["value"] : _ev_0 }), ({  })))], [_ev_0], ({  })))), [addEvents, ReflexEvent])

  return (
    jsx(RadixThemesCheckbox,{checked:reflex___state____state__warframe_reflex___state____calculator_state.slot_conditions_enabled_rx_state_?.at?.(0),className:"conditional-checkbox-control",onCheckedChange:on_change_6730515b99e8e4e3ead73c5362eb824c,size:"2"},)
  )
}


function Text_78df850853ea5e2295da6322bf8a7b5e () {
  const reflex___state____state__warframe_reflex___state____calculator_state = useContext(StateContexts.reflex___state____state__warframe_reflex___state____calculator_state)



  return (
    jsx(RadixThemesText,{as:"p",className:"conditional-checkbox-label"},"Enable conditional: ",reflex___state____state__warframe_reflex___state____calculator_state.slot_condition_labels_rx_state_?.at?.(0))
  )
}


function Fragment_e6984a442aac429d5fcbed2050e9f4e4 () {
  const reflex___state____state__warframe_reflex___state____calculator_state = useContext(StateContexts.reflex___state____state__warframe_reflex___state____calculator_state)



  return (
    jsx(Fragment,{},(reflex___state____state__warframe_reflex___state____calculator_state.slot_has_conditionals_rx_state_?.at?.(0)?(jsx(Fragment,{},jsx(RadixThemesFlex,{align:"start",className:"rx-Stack conditional-checkbox-row",direction:"row",gap:"3"},jsx(RadixThemesText,{as:"label",size:"2"},jsx(RadixThemesFlex,{gap:"2"},jsx(Checkbox_1c9ce19dbbeeac9c110d1988207260dd,{},),"")),jsx(Text_78df850853ea5e2295da6322bf8a7b5e,{},)))):(jsx(Fragment,{},))))
  )
}


function Flex_a41f17da1900d38a2c733272308262d1 () {
  const reflex___state____state__warframe_reflex___state____calculator_state = useContext(StateContexts.reflex___state____state__warframe_reflex___state____calculator_state)



  return (
    jsx(RadixThemesFlex,{align:"start",className:"rx-Stack",css:({ ["width"] : "100%", ["gap"] : "1" }),direction:"column",gap:"3"},Array.prototype.map.call(reflex___state____state__warframe_reflex___state____calculator_state.slot_stat_rows_rx_state_?.at?.(0) ?? [],((row_rx_state_,index_6f0cc146e9e04bdc4ed627113713c33a)=>(jsx(RadixThemesFlex,{align:"center",className:"rx-Stack",css:({ ["width"] : "100%" }),direction:"row",key:index_6f0cc146e9e04bdc4ed627113713c33a,gap:"3"},jsx(RadixThemesText,{as:"p",className:"preview-label"},row_rx_state_?.["label"]),jsx(RadixThemesFlex,{css:({ ["flex"] : 1, ["justifySelf"] : "stretch", ["alignSelf"] : "stretch" })},),jsx(RadixThemesText,{as:"p",className:"preview-value"},row_rx_state_?.["value"]))))))
  )
}


function Fragment_74773811a876286571ca24bcbd2dd361 () {
  const reflex___state____state__warframe_reflex___state____calculator_state = useContext(StateContexts.reflex___state____state__warframe_reflex___state____calculator_state)



  return (
    jsx(Fragment,{},((reflex___state____state__warframe_reflex___state____calculator_state.slot_stat_rows_rx_state_?.at?.(0).length > 0)?(jsx(Fragment,{},jsx(Flex_a41f17da1900d38a2c733272308262d1,{},))):(jsx(Fragment,{},jsx(RadixThemesText,{as:"p",className:"empty-text"},"No stats.")))))
  )
}


function Select__group_f634bb307438e0d55ff5bd4ec4bfa039 () {
  const reflex___state____state__warframe_reflex___state____calculator_state = useContext(StateContexts.reflex___state____state__warframe_reflex___state____calculator_state)



  return (
    jsx(RadixThemesSelect.Group,{},"",Array.prototype.map.call(reflex___state____state__warframe_reflex___state____calculator_state.slot_available_fields_rx_state_?.at?.(0) ?? [],((item_rx_state_,index_d6d6157c99650830f12a866606ea87b7)=>(jsx(RadixThemesSelect.Item,{key:index_d6d6157c99650830f12a866606ea87b7,value:item_rx_state_},item_rx_state_)))))
  )
}


function Select__root_d790cc592caf8aeb3e2fb8e85e345c1b () {
  const reflex___state____state__warframe_reflex___state____calculator_state = useContext(StateContexts.reflex___state____state__warframe_reflex___state____calculator_state)
const [addEvents, connectErrors] = useContext(EventLoopContext);

const on_change_c802b894034e0a7ba32bf862513018bb = useCallback(((_ev_0) => (addEvents([(ReflexEvent("reflex___state____state.warframe_reflex___state____calculator_state.set_slot_pending_field", ({ ["index"] : 0, ["value"] : _ev_0 }), ({  })))], [_ev_0], ({  })))), [addEvents, ReflexEvent])

  return (
    jsx(RadixThemesSelect.Root,{disabled:(reflex___state____state__warframe_reflex___state____calculator_state.slot_available_fields_rx_state_?.at?.(0).length?.valueOf?.() === 0?.valueOf?.()),onValueChange:on_change_c802b894034e0a7ba32bf862513018bb,value:reflex___state____state__warframe_reflex___state____calculator_state.slot_pending_fields_rx_state_?.at?.(0)},jsx(RadixThemesSelect.Trigger,{css:({ ["width"] : "100%" })},),jsx(RadixThemesSelect.Content,{position:"popper"},jsx(Select__group_f634bb307438e0d55ff5bd4ec4bfa039,{},)))
  )
}


function Button_e8c10f3f3845026f32063c8651a7d38a () {
  const reflex___state____state__warframe_reflex___state____calculator_state = useContext(StateContexts.reflex___state____state__warframe_reflex___state____calculator_state)
const [addEvents, connectErrors] = useContext(EventLoopContext);

const on_click_3c5dd42c31b868f1fca73bb5467febc3 = useCallback(((_e) => (addEvents([(ReflexEvent("reflex___state____state.warframe_reflex___state____calculator_state.add_slot_field", ({ ["index"] : 0 }), ({  })))], [_e], ({  })))), [addEvents, ReflexEvent])

  return (
    jsx(RadixThemesButton,{className:"icon-button field-action-button",disabled:(reflex___state____state__warframe_reflex___state____calculator_state.slot_available_fields_rx_state_?.at?.(0).length?.valueOf?.() === 0?.valueOf?.()),onClick:on_click_3c5dd42c31b868f1fca73bb5467febc3},"+")
  )
}


function Flex_b312a5f5228dd647f70b5e24817f6ad9 () {
  const reflex___state____state__warframe_reflex___state____calculator_state = useContext(StateContexts.reflex___state____state__warframe_reflex___state____calculator_state)
const [addEvents, connectErrors] = useContext(EventLoopContext);



  return (
    jsx(RadixThemesFlex,{align:"start",className:"rx-Stack",css:({ ["width"] : "100%", ["gap"] : "2" }),direction:"column",gap:"3"},Array.prototype.map.call(reflex___state____state__warframe_reflex___state____calculator_state.slot_fields_rx_state_?.at?.(0) ?? [],((field_rx_state_,index_ad9d7b81e0e65a5948a3885101cbe585)=>(jsx(RadixThemesGrid,{align:"center",columns:"84px minmax(0, 1fr) 32px",css:({ ["columnGap"] : "8px", ["width"] : "100%" }),key:index_ad9d7b81e0e65a5948a3885101cbe585},jsx(RadixThemesText,{as:"p",className:"compact-label"},field_rx_state_?.["label"]),jsx(DebounceInput,{css:({ ["debounceTimeout"] : 250, ["width"] : "100%" }),debounceTimeout:250,element:RadixThemesTextField.Root,max:field_rx_state_?.["max_value"],min:field_rx_state_?.["min_value"],onChange:((_e) => (addEvents([(ReflexEvent("reflex___state____state.warframe_reflex___state____calculator_state.set_slot_field_value", ({ ["index"] : 0, ["field_name"] : field_rx_state_?.["name"], ["value"] : _e?.["target"]?.["value"] }), ({  })))], [_e], ({  })))),step:(field_rx_state_?.["integer"] ? "1" : "0.001"),type:"number",value:(isNotNullOrUndefined(field_rx_state_?.["value"]) ? field_rx_state_?.["value"] : "")},),jsx(RadixThemesButton,{className:"icon-button field-action-button",onClick:((_e) => (addEvents([(ReflexEvent("reflex___state____state.warframe_reflex___state____calculator_state.remove_slot_field", ({ ["index"] : 0, ["field_name"] : field_rx_state_?.["name"] }), ({  })))], [_e], ({  })))),variant:"soft"},"\u00d7"))))))
  )
}


function Fragment_d8b31ebd44312e224b59a4371cba20e0 () {
  const reflex___state____state__warframe_reflex___state____calculator_state = useContext(StateContexts.reflex___state____state__warframe_reflex___state____calculator_state)



  return (
    jsx(Fragment,{},((reflex___state____state__warframe_reflex___state____calculator_state.slot_fields_rx_state_?.at?.(0).length > 0)?(jsx(Fragment,{},jsx(Flex_b312a5f5228dd647f70b5e24817f6ad9,{},))):(jsx(Fragment,{},jsx(RadixThemesText,{as:"p",className:"empty-text"},"No custom stats added.")))))
  )
}


function Fragment_7e4f4d37efb125abf1e629b89a63993a () {
  const reflex___state____state__warframe_reflex___state____calculator_state = useContext(StateContexts.reflex___state____state__warframe_reflex___state____calculator_state)



  return (
    jsx(Fragment,{},(!((reflex___state____state__warframe_reflex___state____calculator_state.slot_selected_upgrades_rx_state_?.at?.(0)?.valueOf?.() === "Custom"?.valueOf?.()))?(jsx(Fragment,{},jsx(RadixThemesFlex,{align:"start",className:"rx-Stack",css:({ ["width"] : "100%", ["gap"] : "3" }),direction:"column",gap:"3"},jsx(RadixThemesGrid,{columns:"repeat(2, minmax(0, 1fr))",css:({ ["columnGap"] : "8px", ["width"] : "100%" })},jsx(RadixThemesFlex,{align:"start",className:"rx-Stack",css:({ ["gap"] : "1", ["width"] : "100%" }),direction:"column",gap:"3"},jsx(RadixThemesText,{as:"p",className:"field-label"},"Rank"),jsx(Debounceinput_3ce27737ae615357d63b32a9d04184a8,{},)),jsx(Fragment_8342be9ccfb17533524924e8b3c51d19,{},)),jsx(Fragment_e6984a442aac429d5fcbed2050e9f4e4,{},),jsx(RadixThemesSeparator,{css:({ ["width"] : "100%" }),size:"4"},),jsx(Fragment_74773811a876286571ca24bcbd2dd361,{},)))):(jsx(Fragment,{},jsx(RadixThemesFlex,{align:"start",className:"rx-Stack",css:({ ["width"] : "100%", ["gap"] : "3" }),direction:"column",gap:"3"},jsx(RadixThemesGrid,{columns:"minmax(0, 1fr) 32px",css:({ ["columnGap"] : "8px", ["width"] : "100%" })},jsx(Select__root_d790cc592caf8aeb3e2fb8e85e345c1b,{},),jsx(Button_e8c10f3f3845026f32063c8651a7d38a,{},)),jsx(Fragment_d8b31ebd44312e224b59a4371cba20e0,{},),jsx(RadixThemesSeparator,{css:({ ["width"] : "100%" }),size:"4"},),jsx(Fragment_74773811a876286571ca24bcbd2dd361,{},))))))
  )
}


function Badge_a97901c07a3a98a858665408b9134a2d () {
  const reflex___state____state__warframe_reflex___state____calculator_state = useContext(StateContexts.reflex___state____state__warframe_reflex___state____calculator_state)



  return (
    jsx(RadixThemesBadge,{className:"contribution-badge",variant:"soft"},reflex___state____state__warframe_reflex___state____calculator_state.slot_contributions_rx_state_?.at?.(1))
  )
}


function Select__root_b6d728b6bb97202ae0fa1e8c9610183b () {
  const reflex___state____state__warframe_reflex___state____calculator_state = useContext(StateContexts.reflex___state____state__warframe_reflex___state____calculator_state)
const [addEvents, connectErrors] = useContext(EventLoopContext);

const on_change_990c02cdc3d83539921b7ff3b69d6d49 = useCallback(((_ev_0) => (addEvents([(ReflexEvent("reflex___state____state.warframe_reflex___state____calculator_state.set_slot_upgrade", ({ ["index"] : 1, ["value"] : _ev_0 }), ({  })))], [_ev_0], ({  })))), [addEvents, ReflexEvent])

  return (
    jsx(RadixThemesSelect.Root,{onValueChange:on_change_990c02cdc3d83539921b7ff3b69d6d49,value:reflex___state____state__warframe_reflex___state____calculator_state.slot_selected_upgrades_rx_state_?.at?.(1)},jsx(RadixThemesSelect.Trigger,{css:({ ["width"] : "100%" })},),jsx(RadixThemesSelect.Content,{position:"popper"},jsx(Select__group_a3ecac2495351b434ca1713de89fa7a8,{},)))
  )
}


function Debounceinput_d0230760887b6abc085a09666c834149 () {
  const reflex___state____state__warframe_reflex___state____calculator_state = useContext(StateContexts.reflex___state____state__warframe_reflex___state____calculator_state)
const [addEvents, connectErrors] = useContext(EventLoopContext);

const on_change_cc3ed7f99fd1260a747a3f318a90f727 = useCallback(((_e) => (addEvents([(ReflexEvent("reflex___state____state.warframe_reflex___state____calculator_state.set_slot_rank", ({ ["index"] : 1, ["value"] : _e?.["target"]?.["value"] }), ({  })))], [_e], ({  })))), [addEvents, ReflexEvent])

  return (
    jsx(DebounceInput,{css:({ ["width"] : "100%", ["debounceTimeout"] : 250 }),debounceTimeout:250,element:RadixThemesTextField.Root,max:reflex___state____state__warframe_reflex___state____calculator_state.slot_max_ranks_rx_state_?.at?.(1),min:0,onChange:on_change_cc3ed7f99fd1260a747a3f318a90f727,step:"1",type:"number",value:(isNotNullOrUndefined(reflex___state____state__warframe_reflex___state____calculator_state.slot_ranks_rx_state_?.at?.(1)) ? reflex___state____state__warframe_reflex___state____calculator_state.slot_ranks_rx_state_?.at?.(1) : "")},)
  )
}


function Debounceinput_cef665036b23a50533061b93e1ca606b () {
  const reflex___state____state__warframe_reflex___state____calculator_state = useContext(StateContexts.reflex___state____state__warframe_reflex___state____calculator_state)
const [addEvents, connectErrors] = useContext(EventLoopContext);

const on_change_2428b1aa0a33404ab7df573238458bc2 = useCallback(((_e) => (addEvents([(ReflexEvent("reflex___state____state.warframe_reflex___state____calculator_state.set_slot_stacks", ({ ["index"] : 1, ["value"] : _e?.["target"]?.["value"] }), ({  })))], [_e], ({  })))), [addEvents, ReflexEvent])

  return (
    jsx(DebounceInput,{css:({ ["width"] : "100%", ["debounceTimeout"] : 250 }),debounceTimeout:250,element:RadixThemesTextField.Root,max:reflex___state____state__warframe_reflex___state____calculator_state.slot_max_stacks_rx_state_?.at?.(1),min:0,onChange:on_change_2428b1aa0a33404ab7df573238458bc2,step:"1",type:"number",value:(isNotNullOrUndefined(reflex___state____state__warframe_reflex___state____calculator_state.slot_stacks_rx_state_?.at?.(1)) ? reflex___state____state__warframe_reflex___state____calculator_state.slot_stacks_rx_state_?.at?.(1) : "")},)
  )
}


function Fragment_0d1e27e8a97b483044515eb297b7a278 () {
  const reflex___state____state__warframe_reflex___state____calculator_state = useContext(StateContexts.reflex___state____state__warframe_reflex___state____calculator_state)



  return (
    jsx(Fragment,{},((reflex___state____state__warframe_reflex___state____calculator_state.slot_max_stacks_rx_state_?.at?.(1) > 0)?(jsx(Fragment,{},jsx(RadixThemesFlex,{align:"start",className:"rx-Stack",css:({ ["gap"] : "1", ["width"] : "100%" }),direction:"column",gap:"3"},jsx(RadixThemesText,{as:"p",className:"field-label"},"Stacks"),jsx(Debounceinput_cef665036b23a50533061b93e1ca606b,{},)))):(jsx(Fragment,{},))))
  )
}


function Checkbox_391cda5658a69bfe631f6610eb630e01 () {
  const reflex___state____state__warframe_reflex___state____calculator_state = useContext(StateContexts.reflex___state____state__warframe_reflex___state____calculator_state)
const [addEvents, connectErrors] = useContext(EventLoopContext);

const on_change_a91082888abe1f3356c2480f5f2335f1 = useCallback(((_ev_0) => (addEvents([(ReflexEvent("reflex___state____state.warframe_reflex___state____calculator_state.set_slot_condition", ({ ["index"] : 1, ["value"] : _ev_0 }), ({  })))], [_ev_0], ({  })))), [addEvents, ReflexEvent])

  return (
    jsx(RadixThemesCheckbox,{checked:reflex___state____state__warframe_reflex___state____calculator_state.slot_conditions_enabled_rx_state_?.at?.(1),className:"conditional-checkbox-control",onCheckedChange:on_change_a91082888abe1f3356c2480f5f2335f1,size:"2"},)
  )
}


function Text_fff72bff455b0a9207028fa791b447ec () {
  const reflex___state____state__warframe_reflex___state____calculator_state = useContext(StateContexts.reflex___state____state__warframe_reflex___state____calculator_state)



  return (
    jsx(RadixThemesText,{as:"p",className:"conditional-checkbox-label"},"Enable conditional: ",reflex___state____state__warframe_reflex___state____calculator_state.slot_condition_labels_rx_state_?.at?.(1))
  )
}


function Fragment_c811a64491194555a34eb508276f024f () {
  const reflex___state____state__warframe_reflex___state____calculator_state = useContext(StateContexts.reflex___state____state__warframe_reflex___state____calculator_state)



  return (
    jsx(Fragment,{},(reflex___state____state__warframe_reflex___state____calculator_state.slot_has_conditionals_rx_state_?.at?.(1)?(jsx(Fragment,{},jsx(RadixThemesFlex,{align:"start",className:"rx-Stack conditional-checkbox-row",direction:"row",gap:"3"},jsx(RadixThemesText,{as:"label",size:"2"},jsx(RadixThemesFlex,{gap:"2"},jsx(Checkbox_391cda5658a69bfe631f6610eb630e01,{},),"")),jsx(Text_fff72bff455b0a9207028fa791b447ec,{},)))):(jsx(Fragment,{},))))
  )
}


function Flex_28a40665193d37c52577a8eb4143690f () {
  const reflex___state____state__warframe_reflex___state____calculator_state = useContext(StateContexts.reflex___state____state__warframe_reflex___state____calculator_state)



  return (
    jsx(RadixThemesFlex,{align:"start",className:"rx-Stack",css:({ ["width"] : "100%", ["gap"] : "1" }),direction:"column",gap:"3"},Array.prototype.map.call(reflex___state____state__warframe_reflex___state____calculator_state.slot_stat_rows_rx_state_?.at?.(1) ?? [],((row_rx_state_,index_6f0cc146e9e04bdc4ed627113713c33a)=>(jsx(RadixThemesFlex,{align:"center",className:"rx-Stack",css:({ ["width"] : "100%" }),direction:"row",key:index_6f0cc146e9e04bdc4ed627113713c33a,gap:"3"},jsx(RadixThemesText,{as:"p",className:"preview-label"},row_rx_state_?.["label"]),jsx(RadixThemesFlex,{css:({ ["flex"] : 1, ["justifySelf"] : "stretch", ["alignSelf"] : "stretch" })},),jsx(RadixThemesText,{as:"p",className:"preview-value"},row_rx_state_?.["value"]))))))
  )
}


function Fragment_c2ad171ed6455367efadc4cb0524a805 () {
  const reflex___state____state__warframe_reflex___state____calculator_state = useContext(StateContexts.reflex___state____state__warframe_reflex___state____calculator_state)



  return (
    jsx(Fragment,{},((reflex___state____state__warframe_reflex___state____calculator_state.slot_stat_rows_rx_state_?.at?.(1).length > 0)?(jsx(Fragment,{},jsx(Flex_28a40665193d37c52577a8eb4143690f,{},))):(jsx(Fragment,{},jsx(RadixThemesText,{as:"p",className:"empty-text"},"No stats.")))))
  )
}


function Select__group_accbc000f8f93fbfec2a5ff20765815a () {
  const reflex___state____state__warframe_reflex___state____calculator_state = useContext(StateContexts.reflex___state____state__warframe_reflex___state____calculator_state)



  return (
    jsx(RadixThemesSelect.Group,{},"",Array.prototype.map.call(reflex___state____state__warframe_reflex___state____calculator_state.slot_available_fields_rx_state_?.at?.(1) ?? [],((item_rx_state_,index_d6d6157c99650830f12a866606ea87b7)=>(jsx(RadixThemesSelect.Item,{key:index_d6d6157c99650830f12a866606ea87b7,value:item_rx_state_},item_rx_state_)))))
  )
}


function Select__root_9ad6121cc88cadb5caf030716e351980 () {
  const reflex___state____state__warframe_reflex___state____calculator_state = useContext(StateContexts.reflex___state____state__warframe_reflex___state____calculator_state)
const [addEvents, connectErrors] = useContext(EventLoopContext);

const on_change_ec6b6e879d26db2e64bf9c9f7bdd92ce = useCallback(((_ev_0) => (addEvents([(ReflexEvent("reflex___state____state.warframe_reflex___state____calculator_state.set_slot_pending_field", ({ ["index"] : 1, ["value"] : _ev_0 }), ({  })))], [_ev_0], ({  })))), [addEvents, ReflexEvent])

  return (
    jsx(RadixThemesSelect.Root,{disabled:(reflex___state____state__warframe_reflex___state____calculator_state.slot_available_fields_rx_state_?.at?.(1).length?.valueOf?.() === 0?.valueOf?.()),onValueChange:on_change_ec6b6e879d26db2e64bf9c9f7bdd92ce,value:reflex___state____state__warframe_reflex___state____calculator_state.slot_pending_fields_rx_state_?.at?.(1)},jsx(RadixThemesSelect.Trigger,{css:({ ["width"] : "100%" })},),jsx(RadixThemesSelect.Content,{position:"popper"},jsx(Select__group_accbc000f8f93fbfec2a5ff20765815a,{},)))
  )
}


function Button_9ad75ce1bbf813de368723551b6165fc () {
  const reflex___state____state__warframe_reflex___state____calculator_state = useContext(StateContexts.reflex___state____state__warframe_reflex___state____calculator_state)
const [addEvents, connectErrors] = useContext(EventLoopContext);

const on_click_67e047e48c580123760c5b282a798faf = useCallback(((_e) => (addEvents([(ReflexEvent("reflex___state____state.warframe_reflex___state____calculator_state.add_slot_field", ({ ["index"] : 1 }), ({  })))], [_e], ({  })))), [addEvents, ReflexEvent])

  return (
    jsx(RadixThemesButton,{className:"icon-button field-action-button",disabled:(reflex___state____state__warframe_reflex___state____calculator_state.slot_available_fields_rx_state_?.at?.(1).length?.valueOf?.() === 0?.valueOf?.()),onClick:on_click_67e047e48c580123760c5b282a798faf},"+")
  )
}


function Flex_1cda617cf21d95f432e3499ea6abb276 () {
  const reflex___state____state__warframe_reflex___state____calculator_state = useContext(StateContexts.reflex___state____state__warframe_reflex___state____calculator_state)
const [addEvents, connectErrors] = useContext(EventLoopContext);



  return (
    jsx(RadixThemesFlex,{align:"start",className:"rx-Stack",css:({ ["width"] : "100%", ["gap"] : "2" }),direction:"column",gap:"3"},Array.prototype.map.call(reflex___state____state__warframe_reflex___state____calculator_state.slot_fields_rx_state_?.at?.(1) ?? [],((field_rx_state_,index_ad9d7b81e0e65a5948a3885101cbe585)=>(jsx(RadixThemesGrid,{align:"center",columns:"84px minmax(0, 1fr) 32px",css:({ ["columnGap"] : "8px", ["width"] : "100%" }),key:index_ad9d7b81e0e65a5948a3885101cbe585},jsx(RadixThemesText,{as:"p",className:"compact-label"},field_rx_state_?.["label"]),jsx(DebounceInput,{css:({ ["debounceTimeout"] : 250, ["width"] : "100%" }),debounceTimeout:250,element:RadixThemesTextField.Root,max:field_rx_state_?.["max_value"],min:field_rx_state_?.["min_value"],onChange:((_e) => (addEvents([(ReflexEvent("reflex___state____state.warframe_reflex___state____calculator_state.set_slot_field_value", ({ ["index"] : 1, ["field_name"] : field_rx_state_?.["name"], ["value"] : _e?.["target"]?.["value"] }), ({  })))], [_e], ({  })))),step:(field_rx_state_?.["integer"] ? "1" : "0.001"),type:"number",value:(isNotNullOrUndefined(field_rx_state_?.["value"]) ? field_rx_state_?.["value"] : "")},),jsx(RadixThemesButton,{className:"icon-button field-action-button",onClick:((_e) => (addEvents([(ReflexEvent("reflex___state____state.warframe_reflex___state____calculator_state.remove_slot_field", ({ ["index"] : 1, ["field_name"] : field_rx_state_?.["name"] }), ({  })))], [_e], ({  })))),variant:"soft"},"\u00d7"))))))
  )
}


function Fragment_8e0bea3634b133baa61a382a822bcc03 () {
  const reflex___state____state__warframe_reflex___state____calculator_state = useContext(StateContexts.reflex___state____state__warframe_reflex___state____calculator_state)



  return (
    jsx(Fragment,{},((reflex___state____state__warframe_reflex___state____calculator_state.slot_fields_rx_state_?.at?.(1).length > 0)?(jsx(Fragment,{},jsx(Flex_1cda617cf21d95f432e3499ea6abb276,{},))):(jsx(Fragment,{},jsx(RadixThemesText,{as:"p",className:"empty-text"},"No custom stats added.")))))
  )
}


function Fragment_566b4d3a78f405e6f70893fda9071c45 () {
  const reflex___state____state__warframe_reflex___state____calculator_state = useContext(StateContexts.reflex___state____state__warframe_reflex___state____calculator_state)



  return (
    jsx(Fragment,{},(!((reflex___state____state__warframe_reflex___state____calculator_state.slot_selected_upgrades_rx_state_?.at?.(1)?.valueOf?.() === "Custom"?.valueOf?.()))?(jsx(Fragment,{},jsx(RadixThemesFlex,{align:"start",className:"rx-Stack",css:({ ["width"] : "100%", ["gap"] : "3" }),direction:"column",gap:"3"},jsx(RadixThemesGrid,{columns:"repeat(2, minmax(0, 1fr))",css:({ ["columnGap"] : "8px", ["width"] : "100%" })},jsx(RadixThemesFlex,{align:"start",className:"rx-Stack",css:({ ["gap"] : "1", ["width"] : "100%" }),direction:"column",gap:"3"},jsx(RadixThemesText,{as:"p",className:"field-label"},"Rank"),jsx(Debounceinput_d0230760887b6abc085a09666c834149,{},)),jsx(Fragment_0d1e27e8a97b483044515eb297b7a278,{},)),jsx(Fragment_c811a64491194555a34eb508276f024f,{},),jsx(RadixThemesSeparator,{css:({ ["width"] : "100%" }),size:"4"},),jsx(Fragment_c2ad171ed6455367efadc4cb0524a805,{},)))):(jsx(Fragment,{},jsx(RadixThemesFlex,{align:"start",className:"rx-Stack",css:({ ["width"] : "100%", ["gap"] : "3" }),direction:"column",gap:"3"},jsx(RadixThemesGrid,{columns:"minmax(0, 1fr) 32px",css:({ ["columnGap"] : "8px", ["width"] : "100%" })},jsx(Select__root_9ad6121cc88cadb5caf030716e351980,{},),jsx(Button_9ad75ce1bbf813de368723551b6165fc,{},)),jsx(Fragment_8e0bea3634b133baa61a382a822bcc03,{},),jsx(RadixThemesSeparator,{css:({ ["width"] : "100%" }),size:"4"},),jsx(Fragment_c2ad171ed6455367efadc4cb0524a805,{},))))))
  )
}


function Badge_6a03a4e6b5ac6034bd9e918878b6d460 () {
  const reflex___state____state__warframe_reflex___state____calculator_state = useContext(StateContexts.reflex___state____state__warframe_reflex___state____calculator_state)



  return (
    jsx(RadixThemesBadge,{className:"contribution-badge",variant:"soft"},reflex___state____state__warframe_reflex___state____calculator_state.slot_contributions_rx_state_?.at?.(2))
  )
}


function Select__root_f745a1f0dc84f80c24bcb0fe8cacd09a () {
  const reflex___state____state__warframe_reflex___state____calculator_state = useContext(StateContexts.reflex___state____state__warframe_reflex___state____calculator_state)
const [addEvents, connectErrors] = useContext(EventLoopContext);

const on_change_8b05df545d00e8cbbfa56d5c78a6955c = useCallback(((_ev_0) => (addEvents([(ReflexEvent("reflex___state____state.warframe_reflex___state____calculator_state.set_slot_upgrade", ({ ["index"] : 2, ["value"] : _ev_0 }), ({  })))], [_ev_0], ({  })))), [addEvents, ReflexEvent])

  return (
    jsx(RadixThemesSelect.Root,{onValueChange:on_change_8b05df545d00e8cbbfa56d5c78a6955c,value:reflex___state____state__warframe_reflex___state____calculator_state.slot_selected_upgrades_rx_state_?.at?.(2)},jsx(RadixThemesSelect.Trigger,{css:({ ["width"] : "100%" })},),jsx(RadixThemesSelect.Content,{position:"popper"},jsx(Select__group_a3ecac2495351b434ca1713de89fa7a8,{},)))
  )
}


function Debounceinput_85b38755d858cc32a3a755a3c972e8e5 () {
  const reflex___state____state__warframe_reflex___state____calculator_state = useContext(StateContexts.reflex___state____state__warframe_reflex___state____calculator_state)
const [addEvents, connectErrors] = useContext(EventLoopContext);

const on_change_026c37ebe8bddbf4f7dd3d514e9fe934 = useCallback(((_e) => (addEvents([(ReflexEvent("reflex___state____state.warframe_reflex___state____calculator_state.set_slot_rank", ({ ["index"] : 2, ["value"] : _e?.["target"]?.["value"] }), ({  })))], [_e], ({  })))), [addEvents, ReflexEvent])

  return (
    jsx(DebounceInput,{css:({ ["width"] : "100%", ["debounceTimeout"] : 250 }),debounceTimeout:250,element:RadixThemesTextField.Root,max:reflex___state____state__warframe_reflex___state____calculator_state.slot_max_ranks_rx_state_?.at?.(2),min:0,onChange:on_change_026c37ebe8bddbf4f7dd3d514e9fe934,step:"1",type:"number",value:(isNotNullOrUndefined(reflex___state____state__warframe_reflex___state____calculator_state.slot_ranks_rx_state_?.at?.(2)) ? reflex___state____state__warframe_reflex___state____calculator_state.slot_ranks_rx_state_?.at?.(2) : "")},)
  )
}


function Debounceinput_cc64f99a7ba257d3ffc877de9e094f14 () {
  const reflex___state____state__warframe_reflex___state____calculator_state = useContext(StateContexts.reflex___state____state__warframe_reflex___state____calculator_state)
const [addEvents, connectErrors] = useContext(EventLoopContext);

const on_change_1ddaf4a9445b1bc82fb30893529d4c07 = useCallback(((_e) => (addEvents([(ReflexEvent("reflex___state____state.warframe_reflex___state____calculator_state.set_slot_stacks", ({ ["index"] : 2, ["value"] : _e?.["target"]?.["value"] }), ({  })))], [_e], ({  })))), [addEvents, ReflexEvent])

  return (
    jsx(DebounceInput,{css:({ ["width"] : "100%", ["debounceTimeout"] : 250 }),debounceTimeout:250,element:RadixThemesTextField.Root,max:reflex___state____state__warframe_reflex___state____calculator_state.slot_max_stacks_rx_state_?.at?.(2),min:0,onChange:on_change_1ddaf4a9445b1bc82fb30893529d4c07,step:"1",type:"number",value:(isNotNullOrUndefined(reflex___state____state__warframe_reflex___state____calculator_state.slot_stacks_rx_state_?.at?.(2)) ? reflex___state____state__warframe_reflex___state____calculator_state.slot_stacks_rx_state_?.at?.(2) : "")},)
  )
}


function Fragment_e17734cb514a75527bfeb5b75143d970 () {
  const reflex___state____state__warframe_reflex___state____calculator_state = useContext(StateContexts.reflex___state____state__warframe_reflex___state____calculator_state)



  return (
    jsx(Fragment,{},((reflex___state____state__warframe_reflex___state____calculator_state.slot_max_stacks_rx_state_?.at?.(2) > 0)?(jsx(Fragment,{},jsx(RadixThemesFlex,{align:"start",className:"rx-Stack",css:({ ["gap"] : "1", ["width"] : "100%" }),direction:"column",gap:"3"},jsx(RadixThemesText,{as:"p",className:"field-label"},"Stacks"),jsx(Debounceinput_cc64f99a7ba257d3ffc877de9e094f14,{},)))):(jsx(Fragment,{},))))
  )
}


function Checkbox_76ebc3295377106dc26ccc4d3a4909c2 () {
  const reflex___state____state__warframe_reflex___state____calculator_state = useContext(StateContexts.reflex___state____state__warframe_reflex___state____calculator_state)
const [addEvents, connectErrors] = useContext(EventLoopContext);

const on_change_520bda03ea9d4d38dc08873106609181 = useCallback(((_ev_0) => (addEvents([(ReflexEvent("reflex___state____state.warframe_reflex___state____calculator_state.set_slot_condition", ({ ["index"] : 2, ["value"] : _ev_0 }), ({  })))], [_ev_0], ({  })))), [addEvents, ReflexEvent])

  return (
    jsx(RadixThemesCheckbox,{checked:reflex___state____state__warframe_reflex___state____calculator_state.slot_conditions_enabled_rx_state_?.at?.(2),className:"conditional-checkbox-control",onCheckedChange:on_change_520bda03ea9d4d38dc08873106609181,size:"2"},)
  )
}


function Text_1b7f3931f90ac077f1cbbed246aacb68 () {
  const reflex___state____state__warframe_reflex___state____calculator_state = useContext(StateContexts.reflex___state____state__warframe_reflex___state____calculator_state)



  return (
    jsx(RadixThemesText,{as:"p",className:"conditional-checkbox-label"},"Enable conditional: ",reflex___state____state__warframe_reflex___state____calculator_state.slot_condition_labels_rx_state_?.at?.(2))
  )
}


function Fragment_25d57b2e8945b269b8cde3802d8022e0 () {
  const reflex___state____state__warframe_reflex___state____calculator_state = useContext(StateContexts.reflex___state____state__warframe_reflex___state____calculator_state)



  return (
    jsx(Fragment,{},(reflex___state____state__warframe_reflex___state____calculator_state.slot_has_conditionals_rx_state_?.at?.(2)?(jsx(Fragment,{},jsx(RadixThemesFlex,{align:"start",className:"rx-Stack conditional-checkbox-row",direction:"row",gap:"3"},jsx(RadixThemesText,{as:"label",size:"2"},jsx(RadixThemesFlex,{gap:"2"},jsx(Checkbox_76ebc3295377106dc26ccc4d3a4909c2,{},),"")),jsx(Text_1b7f3931f90ac077f1cbbed246aacb68,{},)))):(jsx(Fragment,{},))))
  )
}


function Flex_75afa81e3b82bc6c2b904f8823f61344 () {
  const reflex___state____state__warframe_reflex___state____calculator_state = useContext(StateContexts.reflex___state____state__warframe_reflex___state____calculator_state)



  return (
    jsx(RadixThemesFlex,{align:"start",className:"rx-Stack",css:({ ["width"] : "100%", ["gap"] : "1" }),direction:"column",gap:"3"},Array.prototype.map.call(reflex___state____state__warframe_reflex___state____calculator_state.slot_stat_rows_rx_state_?.at?.(2) ?? [],((row_rx_state_,index_6f0cc146e9e04bdc4ed627113713c33a)=>(jsx(RadixThemesFlex,{align:"center",className:"rx-Stack",css:({ ["width"] : "100%" }),direction:"row",key:index_6f0cc146e9e04bdc4ed627113713c33a,gap:"3"},jsx(RadixThemesText,{as:"p",className:"preview-label"},row_rx_state_?.["label"]),jsx(RadixThemesFlex,{css:({ ["flex"] : 1, ["justifySelf"] : "stretch", ["alignSelf"] : "stretch" })},),jsx(RadixThemesText,{as:"p",className:"preview-value"},row_rx_state_?.["value"]))))))
  )
}


function Fragment_70ea9decaf9ed8c38b9b81db943c99f8 () {
  const reflex___state____state__warframe_reflex___state____calculator_state = useContext(StateContexts.reflex___state____state__warframe_reflex___state____calculator_state)



  return (
    jsx(Fragment,{},((reflex___state____state__warframe_reflex___state____calculator_state.slot_stat_rows_rx_state_?.at?.(2).length > 0)?(jsx(Fragment,{},jsx(Flex_75afa81e3b82bc6c2b904f8823f61344,{},))):(jsx(Fragment,{},jsx(RadixThemesText,{as:"p",className:"empty-text"},"No stats.")))))
  )
}


function Select__group_8e6e2ac02f086dfd82ac8c943863dd6f () {
  const reflex___state____state__warframe_reflex___state____calculator_state = useContext(StateContexts.reflex___state____state__warframe_reflex___state____calculator_state)



  return (
    jsx(RadixThemesSelect.Group,{},"",Array.prototype.map.call(reflex___state____state__warframe_reflex___state____calculator_state.slot_available_fields_rx_state_?.at?.(2) ?? [],((item_rx_state_,index_d6d6157c99650830f12a866606ea87b7)=>(jsx(RadixThemesSelect.Item,{key:index_d6d6157c99650830f12a866606ea87b7,value:item_rx_state_},item_rx_state_)))))
  )
}


function Select__root_7d3b45258b474bab8347ef1c62fd92d8 () {
  const reflex___state____state__warframe_reflex___state____calculator_state = useContext(StateContexts.reflex___state____state__warframe_reflex___state____calculator_state)
const [addEvents, connectErrors] = useContext(EventLoopContext);

const on_change_8d17fcdb0e6e22734d06f99996276141 = useCallback(((_ev_0) => (addEvents([(ReflexEvent("reflex___state____state.warframe_reflex___state____calculator_state.set_slot_pending_field", ({ ["index"] : 2, ["value"] : _ev_0 }), ({  })))], [_ev_0], ({  })))), [addEvents, ReflexEvent])

  return (
    jsx(RadixThemesSelect.Root,{disabled:(reflex___state____state__warframe_reflex___state____calculator_state.slot_available_fields_rx_state_?.at?.(2).length?.valueOf?.() === 0?.valueOf?.()),onValueChange:on_change_8d17fcdb0e6e22734d06f99996276141,value:reflex___state____state__warframe_reflex___state____calculator_state.slot_pending_fields_rx_state_?.at?.(2)},jsx(RadixThemesSelect.Trigger,{css:({ ["width"] : "100%" })},),jsx(RadixThemesSelect.Content,{position:"popper"},jsx(Select__group_8e6e2ac02f086dfd82ac8c943863dd6f,{},)))
  )
}


function Button_41f0d755ca82d0f1bb552c2dcf2c9ec8 () {
  const reflex___state____state__warframe_reflex___state____calculator_state = useContext(StateContexts.reflex___state____state__warframe_reflex___state____calculator_state)
const [addEvents, connectErrors] = useContext(EventLoopContext);

const on_click_006486446b191fc1d79b4d900ee6afcc = useCallback(((_e) => (addEvents([(ReflexEvent("reflex___state____state.warframe_reflex___state____calculator_state.add_slot_field", ({ ["index"] : 2 }), ({  })))], [_e], ({  })))), [addEvents, ReflexEvent])

  return (
    jsx(RadixThemesButton,{className:"icon-button field-action-button",disabled:(reflex___state____state__warframe_reflex___state____calculator_state.slot_available_fields_rx_state_?.at?.(2).length?.valueOf?.() === 0?.valueOf?.()),onClick:on_click_006486446b191fc1d79b4d900ee6afcc},"+")
  )
}


function Flex_4340d3ec8b42c492065c33b43eb278c9 () {
  const reflex___state____state__warframe_reflex___state____calculator_state = useContext(StateContexts.reflex___state____state__warframe_reflex___state____calculator_state)
const [addEvents, connectErrors] = useContext(EventLoopContext);



  return (
    jsx(RadixThemesFlex,{align:"start",className:"rx-Stack",css:({ ["width"] : "100%", ["gap"] : "2" }),direction:"column",gap:"3"},Array.prototype.map.call(reflex___state____state__warframe_reflex___state____calculator_state.slot_fields_rx_state_?.at?.(2) ?? [],((field_rx_state_,index_ad9d7b81e0e65a5948a3885101cbe585)=>(jsx(RadixThemesGrid,{align:"center",columns:"84px minmax(0, 1fr) 32px",css:({ ["columnGap"] : "8px", ["width"] : "100%" }),key:index_ad9d7b81e0e65a5948a3885101cbe585},jsx(RadixThemesText,{as:"p",className:"compact-label"},field_rx_state_?.["label"]),jsx(DebounceInput,{css:({ ["debounceTimeout"] : 250, ["width"] : "100%" }),debounceTimeout:250,element:RadixThemesTextField.Root,max:field_rx_state_?.["max_value"],min:field_rx_state_?.["min_value"],onChange:((_e) => (addEvents([(ReflexEvent("reflex___state____state.warframe_reflex___state____calculator_state.set_slot_field_value", ({ ["index"] : 2, ["field_name"] : field_rx_state_?.["name"], ["value"] : _e?.["target"]?.["value"] }), ({  })))], [_e], ({  })))),step:(field_rx_state_?.["integer"] ? "1" : "0.001"),type:"number",value:(isNotNullOrUndefined(field_rx_state_?.["value"]) ? field_rx_state_?.["value"] : "")},),jsx(RadixThemesButton,{className:"icon-button field-action-button",onClick:((_e) => (addEvents([(ReflexEvent("reflex___state____state.warframe_reflex___state____calculator_state.remove_slot_field", ({ ["index"] : 2, ["field_name"] : field_rx_state_?.["name"] }), ({  })))], [_e], ({  })))),variant:"soft"},"\u00d7"))))))
  )
}


function Fragment_a7f31d9a0e0444e2ee7701d12237c4f4 () {
  const reflex___state____state__warframe_reflex___state____calculator_state = useContext(StateContexts.reflex___state____state__warframe_reflex___state____calculator_state)



  return (
    jsx(Fragment,{},((reflex___state____state__warframe_reflex___state____calculator_state.slot_fields_rx_state_?.at?.(2).length > 0)?(jsx(Fragment,{},jsx(Flex_4340d3ec8b42c492065c33b43eb278c9,{},))):(jsx(Fragment,{},jsx(RadixThemesText,{as:"p",className:"empty-text"},"No custom stats added.")))))
  )
}


function Fragment_ac0c352ad312f583f91e22b28de07a23 () {
  const reflex___state____state__warframe_reflex___state____calculator_state = useContext(StateContexts.reflex___state____state__warframe_reflex___state____calculator_state)



  return (
    jsx(Fragment,{},(!((reflex___state____state__warframe_reflex___state____calculator_state.slot_selected_upgrades_rx_state_?.at?.(2)?.valueOf?.() === "Custom"?.valueOf?.()))?(jsx(Fragment,{},jsx(RadixThemesFlex,{align:"start",className:"rx-Stack",css:({ ["width"] : "100%", ["gap"] : "3" }),direction:"column",gap:"3"},jsx(RadixThemesGrid,{columns:"repeat(2, minmax(0, 1fr))",css:({ ["columnGap"] : "8px", ["width"] : "100%" })},jsx(RadixThemesFlex,{align:"start",className:"rx-Stack",css:({ ["gap"] : "1", ["width"] : "100%" }),direction:"column",gap:"3"},jsx(RadixThemesText,{as:"p",className:"field-label"},"Rank"),jsx(Debounceinput_85b38755d858cc32a3a755a3c972e8e5,{},)),jsx(Fragment_e17734cb514a75527bfeb5b75143d970,{},)),jsx(Fragment_25d57b2e8945b269b8cde3802d8022e0,{},),jsx(RadixThemesSeparator,{css:({ ["width"] : "100%" }),size:"4"},),jsx(Fragment_70ea9decaf9ed8c38b9b81db943c99f8,{},)))):(jsx(Fragment,{},jsx(RadixThemesFlex,{align:"start",className:"rx-Stack",css:({ ["width"] : "100%", ["gap"] : "3" }),direction:"column",gap:"3"},jsx(RadixThemesGrid,{columns:"minmax(0, 1fr) 32px",css:({ ["columnGap"] : "8px", ["width"] : "100%" })},jsx(Select__root_7d3b45258b474bab8347ef1c62fd92d8,{},),jsx(Button_41f0d755ca82d0f1bb552c2dcf2c9ec8,{},)),jsx(Fragment_a7f31d9a0e0444e2ee7701d12237c4f4,{},),jsx(RadixThemesSeparator,{css:({ ["width"] : "100%" }),size:"4"},),jsx(Fragment_70ea9decaf9ed8c38b9b81db943c99f8,{},))))))
  )
}


function Badge_de4591d81d49141ed8b1977917dbd4c4 () {
  const reflex___state____state__warframe_reflex___state____calculator_state = useContext(StateContexts.reflex___state____state__warframe_reflex___state____calculator_state)



  return (
    jsx(RadixThemesBadge,{className:"contribution-badge",variant:"soft"},reflex___state____state__warframe_reflex___state____calculator_state.slot_contributions_rx_state_?.at?.(3))
  )
}


function Select__root_338de6cda39202a4fb0acc86b51c9331 () {
  const reflex___state____state__warframe_reflex___state____calculator_state = useContext(StateContexts.reflex___state____state__warframe_reflex___state____calculator_state)
const [addEvents, connectErrors] = useContext(EventLoopContext);

const on_change_776f2c55535141304414c99cbfca9280 = useCallback(((_ev_0) => (addEvents([(ReflexEvent("reflex___state____state.warframe_reflex___state____calculator_state.set_slot_upgrade", ({ ["index"] : 3, ["value"] : _ev_0 }), ({  })))], [_ev_0], ({  })))), [addEvents, ReflexEvent])

  return (
    jsx(RadixThemesSelect.Root,{onValueChange:on_change_776f2c55535141304414c99cbfca9280,value:reflex___state____state__warframe_reflex___state____calculator_state.slot_selected_upgrades_rx_state_?.at?.(3)},jsx(RadixThemesSelect.Trigger,{css:({ ["width"] : "100%" })},),jsx(RadixThemesSelect.Content,{position:"popper"},jsx(Select__group_a3ecac2495351b434ca1713de89fa7a8,{},)))
  )
}


function Debounceinput_8f621e866be3015591bde2380c136ee3 () {
  const reflex___state____state__warframe_reflex___state____calculator_state = useContext(StateContexts.reflex___state____state__warframe_reflex___state____calculator_state)
const [addEvents, connectErrors] = useContext(EventLoopContext);

const on_change_9a3f424db2880411d792608adcd25034 = useCallback(((_e) => (addEvents([(ReflexEvent("reflex___state____state.warframe_reflex___state____calculator_state.set_slot_rank", ({ ["index"] : 3, ["value"] : _e?.["target"]?.["value"] }), ({  })))], [_e], ({  })))), [addEvents, ReflexEvent])

  return (
    jsx(DebounceInput,{css:({ ["width"] : "100%", ["debounceTimeout"] : 250 }),debounceTimeout:250,element:RadixThemesTextField.Root,max:reflex___state____state__warframe_reflex___state____calculator_state.slot_max_ranks_rx_state_?.at?.(3),min:0,onChange:on_change_9a3f424db2880411d792608adcd25034,step:"1",type:"number",value:(isNotNullOrUndefined(reflex___state____state__warframe_reflex___state____calculator_state.slot_ranks_rx_state_?.at?.(3)) ? reflex___state____state__warframe_reflex___state____calculator_state.slot_ranks_rx_state_?.at?.(3) : "")},)
  )
}


function Debounceinput_b37b4a45a4d72d34f108cbde89a4a2c7 () {
  const reflex___state____state__warframe_reflex___state____calculator_state = useContext(StateContexts.reflex___state____state__warframe_reflex___state____calculator_state)
const [addEvents, connectErrors] = useContext(EventLoopContext);

const on_change_8014fa4a7eeb99e59d8eaea9ed7bca17 = useCallback(((_e) => (addEvents([(ReflexEvent("reflex___state____state.warframe_reflex___state____calculator_state.set_slot_stacks", ({ ["index"] : 3, ["value"] : _e?.["target"]?.["value"] }), ({  })))], [_e], ({  })))), [addEvents, ReflexEvent])

  return (
    jsx(DebounceInput,{css:({ ["width"] : "100%", ["debounceTimeout"] : 250 }),debounceTimeout:250,element:RadixThemesTextField.Root,max:reflex___state____state__warframe_reflex___state____calculator_state.slot_max_stacks_rx_state_?.at?.(3),min:0,onChange:on_change_8014fa4a7eeb99e59d8eaea9ed7bca17,step:"1",type:"number",value:(isNotNullOrUndefined(reflex___state____state__warframe_reflex___state____calculator_state.slot_stacks_rx_state_?.at?.(3)) ? reflex___state____state__warframe_reflex___state____calculator_state.slot_stacks_rx_state_?.at?.(3) : "")},)
  )
}


function Fragment_a32b446473c5a00ba2dcb43e6ab1a40f () {
  const reflex___state____state__warframe_reflex___state____calculator_state = useContext(StateContexts.reflex___state____state__warframe_reflex___state____calculator_state)



  return (
    jsx(Fragment,{},((reflex___state____state__warframe_reflex___state____calculator_state.slot_max_stacks_rx_state_?.at?.(3) > 0)?(jsx(Fragment,{},jsx(RadixThemesFlex,{align:"start",className:"rx-Stack",css:({ ["gap"] : "1", ["width"] : "100%" }),direction:"column",gap:"3"},jsx(RadixThemesText,{as:"p",className:"field-label"},"Stacks"),jsx(Debounceinput_b37b4a45a4d72d34f108cbde89a4a2c7,{},)))):(jsx(Fragment,{},))))
  )
}


function Checkbox_1e6d3186b2d6bf49db6a74d9dbcb712f () {
  const reflex___state____state__warframe_reflex___state____calculator_state = useContext(StateContexts.reflex___state____state__warframe_reflex___state____calculator_state)
const [addEvents, connectErrors] = useContext(EventLoopContext);

const on_change_e9b0a328c8147089225de0119959f7be = useCallback(((_ev_0) => (addEvents([(ReflexEvent("reflex___state____state.warframe_reflex___state____calculator_state.set_slot_condition", ({ ["index"] : 3, ["value"] : _ev_0 }), ({  })))], [_ev_0], ({  })))), [addEvents, ReflexEvent])

  return (
    jsx(RadixThemesCheckbox,{checked:reflex___state____state__warframe_reflex___state____calculator_state.slot_conditions_enabled_rx_state_?.at?.(3),className:"conditional-checkbox-control",onCheckedChange:on_change_e9b0a328c8147089225de0119959f7be,size:"2"},)
  )
}


function Text_e76dcfc84b7d2869dd2f964344411231 () {
  const reflex___state____state__warframe_reflex___state____calculator_state = useContext(StateContexts.reflex___state____state__warframe_reflex___state____calculator_state)



  return (
    jsx(RadixThemesText,{as:"p",className:"conditional-checkbox-label"},"Enable conditional: ",reflex___state____state__warframe_reflex___state____calculator_state.slot_condition_labels_rx_state_?.at?.(3))
  )
}


function Fragment_983841216124fdf195d30f8a65951706 () {
  const reflex___state____state__warframe_reflex___state____calculator_state = useContext(StateContexts.reflex___state____state__warframe_reflex___state____calculator_state)



  return (
    jsx(Fragment,{},(reflex___state____state__warframe_reflex___state____calculator_state.slot_has_conditionals_rx_state_?.at?.(3)?(jsx(Fragment,{},jsx(RadixThemesFlex,{align:"start",className:"rx-Stack conditional-checkbox-row",direction:"row",gap:"3"},jsx(RadixThemesText,{as:"label",size:"2"},jsx(RadixThemesFlex,{gap:"2"},jsx(Checkbox_1e6d3186b2d6bf49db6a74d9dbcb712f,{},),"")),jsx(Text_e76dcfc84b7d2869dd2f964344411231,{},)))):(jsx(Fragment,{},))))
  )
}


function Flex_16c41f09ff1210092e3b8872055f3fb5 () {
  const reflex___state____state__warframe_reflex___state____calculator_state = useContext(StateContexts.reflex___state____state__warframe_reflex___state____calculator_state)



  return (
    jsx(RadixThemesFlex,{align:"start",className:"rx-Stack",css:({ ["width"] : "100%", ["gap"] : "1" }),direction:"column",gap:"3"},Array.prototype.map.call(reflex___state____state__warframe_reflex___state____calculator_state.slot_stat_rows_rx_state_?.at?.(3) ?? [],((row_rx_state_,index_6f0cc146e9e04bdc4ed627113713c33a)=>(jsx(RadixThemesFlex,{align:"center",className:"rx-Stack",css:({ ["width"] : "100%" }),direction:"row",key:index_6f0cc146e9e04bdc4ed627113713c33a,gap:"3"},jsx(RadixThemesText,{as:"p",className:"preview-label"},row_rx_state_?.["label"]),jsx(RadixThemesFlex,{css:({ ["flex"] : 1, ["justifySelf"] : "stretch", ["alignSelf"] : "stretch" })},),jsx(RadixThemesText,{as:"p",className:"preview-value"},row_rx_state_?.["value"]))))))
  )
}


function Fragment_35b30deda803a5417a185f27885bd3e6 () {
  const reflex___state____state__warframe_reflex___state____calculator_state = useContext(StateContexts.reflex___state____state__warframe_reflex___state____calculator_state)



  return (
    jsx(Fragment,{},((reflex___state____state__warframe_reflex___state____calculator_state.slot_stat_rows_rx_state_?.at?.(3).length > 0)?(jsx(Fragment,{},jsx(Flex_16c41f09ff1210092e3b8872055f3fb5,{},))):(jsx(Fragment,{},jsx(RadixThemesText,{as:"p",className:"empty-text"},"No stats.")))))
  )
}


function Select__group_d05a86ee3ac765b38490efee23fcb880 () {
  const reflex___state____state__warframe_reflex___state____calculator_state = useContext(StateContexts.reflex___state____state__warframe_reflex___state____calculator_state)



  return (
    jsx(RadixThemesSelect.Group,{},"",Array.prototype.map.call(reflex___state____state__warframe_reflex___state____calculator_state.slot_available_fields_rx_state_?.at?.(3) ?? [],((item_rx_state_,index_d6d6157c99650830f12a866606ea87b7)=>(jsx(RadixThemesSelect.Item,{key:index_d6d6157c99650830f12a866606ea87b7,value:item_rx_state_},item_rx_state_)))))
  )
}


function Select__root_a767d58af42023f278e796c013161e96 () {
  const reflex___state____state__warframe_reflex___state____calculator_state = useContext(StateContexts.reflex___state____state__warframe_reflex___state____calculator_state)
const [addEvents, connectErrors] = useContext(EventLoopContext);

const on_change_3268a23319b2f6ba4c194c0e4618d15c = useCallback(((_ev_0) => (addEvents([(ReflexEvent("reflex___state____state.warframe_reflex___state____calculator_state.set_slot_pending_field", ({ ["index"] : 3, ["value"] : _ev_0 }), ({  })))], [_ev_0], ({  })))), [addEvents, ReflexEvent])

  return (
    jsx(RadixThemesSelect.Root,{disabled:(reflex___state____state__warframe_reflex___state____calculator_state.slot_available_fields_rx_state_?.at?.(3).length?.valueOf?.() === 0?.valueOf?.()),onValueChange:on_change_3268a23319b2f6ba4c194c0e4618d15c,value:reflex___state____state__warframe_reflex___state____calculator_state.slot_pending_fields_rx_state_?.at?.(3)},jsx(RadixThemesSelect.Trigger,{css:({ ["width"] : "100%" })},),jsx(RadixThemesSelect.Content,{position:"popper"},jsx(Select__group_d05a86ee3ac765b38490efee23fcb880,{},)))
  )
}


function Button_7ff48c3ffd8033246afd68b42b95544d () {
  const reflex___state____state__warframe_reflex___state____calculator_state = useContext(StateContexts.reflex___state____state__warframe_reflex___state____calculator_state)
const [addEvents, connectErrors] = useContext(EventLoopContext);

const on_click_b5ac7153fbb2fc09778f57e275d52836 = useCallback(((_e) => (addEvents([(ReflexEvent("reflex___state____state.warframe_reflex___state____calculator_state.add_slot_field", ({ ["index"] : 3 }), ({  })))], [_e], ({  })))), [addEvents, ReflexEvent])

  return (
    jsx(RadixThemesButton,{className:"icon-button field-action-button",disabled:(reflex___state____state__warframe_reflex___state____calculator_state.slot_available_fields_rx_state_?.at?.(3).length?.valueOf?.() === 0?.valueOf?.()),onClick:on_click_b5ac7153fbb2fc09778f57e275d52836},"+")
  )
}


function Flex_c47e8b8ceacc4d257885c7ec149ad75d () {
  const reflex___state____state__warframe_reflex___state____calculator_state = useContext(StateContexts.reflex___state____state__warframe_reflex___state____calculator_state)
const [addEvents, connectErrors] = useContext(EventLoopContext);



  return (
    jsx(RadixThemesFlex,{align:"start",className:"rx-Stack",css:({ ["width"] : "100%", ["gap"] : "2" }),direction:"column",gap:"3"},Array.prototype.map.call(reflex___state____state__warframe_reflex___state____calculator_state.slot_fields_rx_state_?.at?.(3) ?? [],((field_rx_state_,index_ad9d7b81e0e65a5948a3885101cbe585)=>(jsx(RadixThemesGrid,{align:"center",columns:"84px minmax(0, 1fr) 32px",css:({ ["columnGap"] : "8px", ["width"] : "100%" }),key:index_ad9d7b81e0e65a5948a3885101cbe585},jsx(RadixThemesText,{as:"p",className:"compact-label"},field_rx_state_?.["label"]),jsx(DebounceInput,{css:({ ["debounceTimeout"] : 250, ["width"] : "100%" }),debounceTimeout:250,element:RadixThemesTextField.Root,max:field_rx_state_?.["max_value"],min:field_rx_state_?.["min_value"],onChange:((_e) => (addEvents([(ReflexEvent("reflex___state____state.warframe_reflex___state____calculator_state.set_slot_field_value", ({ ["index"] : 3, ["field_name"] : field_rx_state_?.["name"], ["value"] : _e?.["target"]?.["value"] }), ({  })))], [_e], ({  })))),step:(field_rx_state_?.["integer"] ? "1" : "0.001"),type:"number",value:(isNotNullOrUndefined(field_rx_state_?.["value"]) ? field_rx_state_?.["value"] : "")},),jsx(RadixThemesButton,{className:"icon-button field-action-button",onClick:((_e) => (addEvents([(ReflexEvent("reflex___state____state.warframe_reflex___state____calculator_state.remove_slot_field", ({ ["index"] : 3, ["field_name"] : field_rx_state_?.["name"] }), ({  })))], [_e], ({  })))),variant:"soft"},"\u00d7"))))))
  )
}


function Fragment_470eecd525edf52e390c1c9d3ad13b8e () {
  const reflex___state____state__warframe_reflex___state____calculator_state = useContext(StateContexts.reflex___state____state__warframe_reflex___state____calculator_state)



  return (
    jsx(Fragment,{},((reflex___state____state__warframe_reflex___state____calculator_state.slot_fields_rx_state_?.at?.(3).length > 0)?(jsx(Fragment,{},jsx(Flex_c47e8b8ceacc4d257885c7ec149ad75d,{},))):(jsx(Fragment,{},jsx(RadixThemesText,{as:"p",className:"empty-text"},"No custom stats added.")))))
  )
}


function Fragment_11fe049af6ea1345559ed00f89841913 () {
  const reflex___state____state__warframe_reflex___state____calculator_state = useContext(StateContexts.reflex___state____state__warframe_reflex___state____calculator_state)



  return (
    jsx(Fragment,{},(!((reflex___state____state__warframe_reflex___state____calculator_state.slot_selected_upgrades_rx_state_?.at?.(3)?.valueOf?.() === "Custom"?.valueOf?.()))?(jsx(Fragment,{},jsx(RadixThemesFlex,{align:"start",className:"rx-Stack",css:({ ["width"] : "100%", ["gap"] : "3" }),direction:"column",gap:"3"},jsx(RadixThemesGrid,{columns:"repeat(2, minmax(0, 1fr))",css:({ ["columnGap"] : "8px", ["width"] : "100%" })},jsx(RadixThemesFlex,{align:"start",className:"rx-Stack",css:({ ["gap"] : "1", ["width"] : "100%" }),direction:"column",gap:"3"},jsx(RadixThemesText,{as:"p",className:"field-label"},"Rank"),jsx(Debounceinput_8f621e866be3015591bde2380c136ee3,{},)),jsx(Fragment_a32b446473c5a00ba2dcb43e6ab1a40f,{},)),jsx(Fragment_983841216124fdf195d30f8a65951706,{},),jsx(RadixThemesSeparator,{css:({ ["width"] : "100%" }),size:"4"},),jsx(Fragment_35b30deda803a5417a185f27885bd3e6,{},)))):(jsx(Fragment,{},jsx(RadixThemesFlex,{align:"start",className:"rx-Stack",css:({ ["width"] : "100%", ["gap"] : "3" }),direction:"column",gap:"3"},jsx(RadixThemesGrid,{columns:"minmax(0, 1fr) 32px",css:({ ["columnGap"] : "8px", ["width"] : "100%" })},jsx(Select__root_a767d58af42023f278e796c013161e96,{},),jsx(Button_7ff48c3ffd8033246afd68b42b95544d,{},)),jsx(Fragment_470eecd525edf52e390c1c9d3ad13b8e,{},),jsx(RadixThemesSeparator,{css:({ ["width"] : "100%" }),size:"4"},),jsx(Fragment_35b30deda803a5417a185f27885bd3e6,{},))))))
  )
}


function Badge_6b974f8a0b178d20d5c837243116943b () {
  const reflex___state____state__warframe_reflex___state____calculator_state = useContext(StateContexts.reflex___state____state__warframe_reflex___state____calculator_state)



  return (
    jsx(RadixThemesBadge,{className:"contribution-badge",variant:"soft"},reflex___state____state__warframe_reflex___state____calculator_state.slot_contributions_rx_state_?.at?.(4))
  )
}


function Select__group_49d7375e41384ca87bf2ea5f3dee750f () {
  const reflex___state____state__warframe_reflex___state____calculator_state = useContext(StateContexts.reflex___state____state__warframe_reflex___state____calculator_state)



  return (
    jsx(RadixThemesSelect.Group,{},"",Array.prototype.map.call(reflex___state____state__warframe_reflex___state____calculator_state.arcane_options_rx_state_ ?? [],((item_rx_state_,index_d6d6157c99650830f12a866606ea87b7)=>(jsx(RadixThemesSelect.Item,{key:index_d6d6157c99650830f12a866606ea87b7,value:item_rx_state_},item_rx_state_)))))
  )
}


function Select__root_5a3f33e973dacefa80adf7583ad3ff8e () {
  const reflex___state____state__warframe_reflex___state____calculator_state = useContext(StateContexts.reflex___state____state__warframe_reflex___state____calculator_state)
const [addEvents, connectErrors] = useContext(EventLoopContext);

const on_change_8db2ae2e851072d0a8384594fc26f812 = useCallback(((_ev_0) => (addEvents([(ReflexEvent("reflex___state____state.warframe_reflex___state____calculator_state.set_slot_upgrade", ({ ["index"] : 4, ["value"] : _ev_0 }), ({  })))], [_ev_0], ({  })))), [addEvents, ReflexEvent])

  return (
    jsx(RadixThemesSelect.Root,{onValueChange:on_change_8db2ae2e851072d0a8384594fc26f812,value:reflex___state____state__warframe_reflex___state____calculator_state.slot_selected_upgrades_rx_state_?.at?.(4)},jsx(RadixThemesSelect.Trigger,{css:({ ["width"] : "100%" })},),jsx(RadixThemesSelect.Content,{position:"popper"},jsx(Select__group_49d7375e41384ca87bf2ea5f3dee750f,{},)))
  )
}


function Debounceinput_46f02e3e5e046c9263eed21226c7ea85 () {
  const reflex___state____state__warframe_reflex___state____calculator_state = useContext(StateContexts.reflex___state____state__warframe_reflex___state____calculator_state)
const [addEvents, connectErrors] = useContext(EventLoopContext);

const on_change_9172d1a8ad8c97492c5beb2b70cecc5d = useCallback(((_e) => (addEvents([(ReflexEvent("reflex___state____state.warframe_reflex___state____calculator_state.set_slot_rank", ({ ["index"] : 4, ["value"] : _e?.["target"]?.["value"] }), ({  })))], [_e], ({  })))), [addEvents, ReflexEvent])

  return (
    jsx(DebounceInput,{css:({ ["width"] : "100%", ["debounceTimeout"] : 250 }),debounceTimeout:250,element:RadixThemesTextField.Root,max:reflex___state____state__warframe_reflex___state____calculator_state.slot_max_ranks_rx_state_?.at?.(4),min:0,onChange:on_change_9172d1a8ad8c97492c5beb2b70cecc5d,step:"1",type:"number",value:(isNotNullOrUndefined(reflex___state____state__warframe_reflex___state____calculator_state.slot_ranks_rx_state_?.at?.(4)) ? reflex___state____state__warframe_reflex___state____calculator_state.slot_ranks_rx_state_?.at?.(4) : "")},)
  )
}


function Debounceinput_06dd2930d2006fae8823bdbbd0775bcd () {
  const reflex___state____state__warframe_reflex___state____calculator_state = useContext(StateContexts.reflex___state____state__warframe_reflex___state____calculator_state)
const [addEvents, connectErrors] = useContext(EventLoopContext);

const on_change_bc9a692082a893a2957ab220088f8d70 = useCallback(((_e) => (addEvents([(ReflexEvent("reflex___state____state.warframe_reflex___state____calculator_state.set_slot_stacks", ({ ["index"] : 4, ["value"] : _e?.["target"]?.["value"] }), ({  })))], [_e], ({  })))), [addEvents, ReflexEvent])

  return (
    jsx(DebounceInput,{css:({ ["width"] : "100%", ["debounceTimeout"] : 250 }),debounceTimeout:250,element:RadixThemesTextField.Root,max:reflex___state____state__warframe_reflex___state____calculator_state.slot_max_stacks_rx_state_?.at?.(4),min:0,onChange:on_change_bc9a692082a893a2957ab220088f8d70,step:"1",type:"number",value:(isNotNullOrUndefined(reflex___state____state__warframe_reflex___state____calculator_state.slot_stacks_rx_state_?.at?.(4)) ? reflex___state____state__warframe_reflex___state____calculator_state.slot_stacks_rx_state_?.at?.(4) : "")},)
  )
}


function Fragment_f85760e210f5d199c01edad38a532e41 () {
  const reflex___state____state__warframe_reflex___state____calculator_state = useContext(StateContexts.reflex___state____state__warframe_reflex___state____calculator_state)



  return (
    jsx(Fragment,{},((reflex___state____state__warframe_reflex___state____calculator_state.slot_max_stacks_rx_state_?.at?.(4) > 0)?(jsx(Fragment,{},jsx(RadixThemesFlex,{align:"start",className:"rx-Stack",css:({ ["gap"] : "1", ["width"] : "100%" }),direction:"column",gap:"3"},jsx(RadixThemesText,{as:"p",className:"field-label"},"Stacks"),jsx(Debounceinput_06dd2930d2006fae8823bdbbd0775bcd,{},)))):(jsx(Fragment,{},))))
  )
}


function Checkbox_8e544d01ad03225a446a6007799aa369 () {
  const reflex___state____state__warframe_reflex___state____calculator_state = useContext(StateContexts.reflex___state____state__warframe_reflex___state____calculator_state)
const [addEvents, connectErrors] = useContext(EventLoopContext);

const on_change_45e02f21b740e02850dd75dab8be1c4e = useCallback(((_ev_0) => (addEvents([(ReflexEvent("reflex___state____state.warframe_reflex___state____calculator_state.set_slot_condition", ({ ["index"] : 4, ["value"] : _ev_0 }), ({  })))], [_ev_0], ({  })))), [addEvents, ReflexEvent])

  return (
    jsx(RadixThemesCheckbox,{checked:reflex___state____state__warframe_reflex___state____calculator_state.slot_conditions_enabled_rx_state_?.at?.(4),className:"conditional-checkbox-control",onCheckedChange:on_change_45e02f21b740e02850dd75dab8be1c4e,size:"2"},)
  )
}


function Text_3dddd7ac8a4ba1e914c7624945dfc3c1 () {
  const reflex___state____state__warframe_reflex___state____calculator_state = useContext(StateContexts.reflex___state____state__warframe_reflex___state____calculator_state)



  return (
    jsx(RadixThemesText,{as:"p",className:"conditional-checkbox-label"},"Enable conditional: ",reflex___state____state__warframe_reflex___state____calculator_state.slot_condition_labels_rx_state_?.at?.(4))
  )
}


function Fragment_4fc28b488cfca806c00b948e30207280 () {
  const reflex___state____state__warframe_reflex___state____calculator_state = useContext(StateContexts.reflex___state____state__warframe_reflex___state____calculator_state)



  return (
    jsx(Fragment,{},(reflex___state____state__warframe_reflex___state____calculator_state.slot_has_conditionals_rx_state_?.at?.(4)?(jsx(Fragment,{},jsx(RadixThemesFlex,{align:"start",className:"rx-Stack conditional-checkbox-row",direction:"row",gap:"3"},jsx(RadixThemesText,{as:"label",size:"2"},jsx(RadixThemesFlex,{gap:"2"},jsx(Checkbox_8e544d01ad03225a446a6007799aa369,{},),"")),jsx(Text_3dddd7ac8a4ba1e914c7624945dfc3c1,{},)))):(jsx(Fragment,{},))))
  )
}


function Flex_1949ba91ed0d1e72a0637ff68e759647 () {
  const reflex___state____state__warframe_reflex___state____calculator_state = useContext(StateContexts.reflex___state____state__warframe_reflex___state____calculator_state)



  return (
    jsx(RadixThemesFlex,{align:"start",className:"rx-Stack",css:({ ["width"] : "100%", ["gap"] : "1" }),direction:"column",gap:"3"},Array.prototype.map.call(reflex___state____state__warframe_reflex___state____calculator_state.slot_stat_rows_rx_state_?.at?.(4) ?? [],((row_rx_state_,index_6f0cc146e9e04bdc4ed627113713c33a)=>(jsx(RadixThemesFlex,{align:"center",className:"rx-Stack",css:({ ["width"] : "100%" }),direction:"row",key:index_6f0cc146e9e04bdc4ed627113713c33a,gap:"3"},jsx(RadixThemesText,{as:"p",className:"preview-label"},row_rx_state_?.["label"]),jsx(RadixThemesFlex,{css:({ ["flex"] : 1, ["justifySelf"] : "stretch", ["alignSelf"] : "stretch" })},),jsx(RadixThemesText,{as:"p",className:"preview-value"},row_rx_state_?.["value"]))))))
  )
}


function Fragment_71466c6a68ba5e730b37606713a0a708 () {
  const reflex___state____state__warframe_reflex___state____calculator_state = useContext(StateContexts.reflex___state____state__warframe_reflex___state____calculator_state)



  return (
    jsx(Fragment,{},((reflex___state____state__warframe_reflex___state____calculator_state.slot_stat_rows_rx_state_?.at?.(4).length > 0)?(jsx(Fragment,{},jsx(Flex_1949ba91ed0d1e72a0637ff68e759647,{},))):(jsx(Fragment,{},jsx(RadixThemesText,{as:"p",className:"empty-text"},"No stats.")))))
  )
}


function Select__group_e5d44f2493f9ab1ba8cb2571eb5196e7 () {
  const reflex___state____state__warframe_reflex___state____calculator_state = useContext(StateContexts.reflex___state____state__warframe_reflex___state____calculator_state)



  return (
    jsx(RadixThemesSelect.Group,{},"",Array.prototype.map.call(reflex___state____state__warframe_reflex___state____calculator_state.slot_available_fields_rx_state_?.at?.(4) ?? [],((item_rx_state_,index_d6d6157c99650830f12a866606ea87b7)=>(jsx(RadixThemesSelect.Item,{key:index_d6d6157c99650830f12a866606ea87b7,value:item_rx_state_},item_rx_state_)))))
  )
}


function Select__root_6c9a8276e83652a8820d8fe5231a164d () {
  const reflex___state____state__warframe_reflex___state____calculator_state = useContext(StateContexts.reflex___state____state__warframe_reflex___state____calculator_state)
const [addEvents, connectErrors] = useContext(EventLoopContext);

const on_change_dc9c057e54680e75c053d293f2b13c94 = useCallback(((_ev_0) => (addEvents([(ReflexEvent("reflex___state____state.warframe_reflex___state____calculator_state.set_slot_pending_field", ({ ["index"] : 4, ["value"] : _ev_0 }), ({  })))], [_ev_0], ({  })))), [addEvents, ReflexEvent])

  return (
    jsx(RadixThemesSelect.Root,{disabled:(reflex___state____state__warframe_reflex___state____calculator_state.slot_available_fields_rx_state_?.at?.(4).length?.valueOf?.() === 0?.valueOf?.()),onValueChange:on_change_dc9c057e54680e75c053d293f2b13c94,value:reflex___state____state__warframe_reflex___state____calculator_state.slot_pending_fields_rx_state_?.at?.(4)},jsx(RadixThemesSelect.Trigger,{css:({ ["width"] : "100%" })},),jsx(RadixThemesSelect.Content,{position:"popper"},jsx(Select__group_e5d44f2493f9ab1ba8cb2571eb5196e7,{},)))
  )
}


function Button_33a082992cac13dee44a490061b3524c () {
  const reflex___state____state__warframe_reflex___state____calculator_state = useContext(StateContexts.reflex___state____state__warframe_reflex___state____calculator_state)
const [addEvents, connectErrors] = useContext(EventLoopContext);

const on_click_ace03c13cd5e99d355dbaaba2cd7807f = useCallback(((_e) => (addEvents([(ReflexEvent("reflex___state____state.warframe_reflex___state____calculator_state.add_slot_field", ({ ["index"] : 4 }), ({  })))], [_e], ({  })))), [addEvents, ReflexEvent])

  return (
    jsx(RadixThemesButton,{className:"icon-button field-action-button",disabled:(reflex___state____state__warframe_reflex___state____calculator_state.slot_available_fields_rx_state_?.at?.(4).length?.valueOf?.() === 0?.valueOf?.()),onClick:on_click_ace03c13cd5e99d355dbaaba2cd7807f},"+")
  )
}


function Flex_dddcd4bc1375ecc30dad8ec59159ac1d () {
  const reflex___state____state__warframe_reflex___state____calculator_state = useContext(StateContexts.reflex___state____state__warframe_reflex___state____calculator_state)
const [addEvents, connectErrors] = useContext(EventLoopContext);



  return (
    jsx(RadixThemesFlex,{align:"start",className:"rx-Stack",css:({ ["width"] : "100%", ["gap"] : "2" }),direction:"column",gap:"3"},Array.prototype.map.call(reflex___state____state__warframe_reflex___state____calculator_state.slot_fields_rx_state_?.at?.(4) ?? [],((field_rx_state_,index_ad9d7b81e0e65a5948a3885101cbe585)=>(jsx(RadixThemesGrid,{align:"center",columns:"84px minmax(0, 1fr) 32px",css:({ ["columnGap"] : "8px", ["width"] : "100%" }),key:index_ad9d7b81e0e65a5948a3885101cbe585},jsx(RadixThemesText,{as:"p",className:"compact-label"},field_rx_state_?.["label"]),jsx(DebounceInput,{css:({ ["debounceTimeout"] : 250, ["width"] : "100%" }),debounceTimeout:250,element:RadixThemesTextField.Root,max:field_rx_state_?.["max_value"],min:field_rx_state_?.["min_value"],onChange:((_e) => (addEvents([(ReflexEvent("reflex___state____state.warframe_reflex___state____calculator_state.set_slot_field_value", ({ ["index"] : 4, ["field_name"] : field_rx_state_?.["name"], ["value"] : _e?.["target"]?.["value"] }), ({  })))], [_e], ({  })))),step:(field_rx_state_?.["integer"] ? "1" : "0.001"),type:"number",value:(isNotNullOrUndefined(field_rx_state_?.["value"]) ? field_rx_state_?.["value"] : "")},),jsx(RadixThemesButton,{className:"icon-button field-action-button",onClick:((_e) => (addEvents([(ReflexEvent("reflex___state____state.warframe_reflex___state____calculator_state.remove_slot_field", ({ ["index"] : 4, ["field_name"] : field_rx_state_?.["name"] }), ({  })))], [_e], ({  })))),variant:"soft"},"\u00d7"))))))
  )
}


function Fragment_4ea8bb53193dd301c5cfa443c6b6a03b () {
  const reflex___state____state__warframe_reflex___state____calculator_state = useContext(StateContexts.reflex___state____state__warframe_reflex___state____calculator_state)



  return (
    jsx(Fragment,{},((reflex___state____state__warframe_reflex___state____calculator_state.slot_fields_rx_state_?.at?.(4).length > 0)?(jsx(Fragment,{},jsx(Flex_dddcd4bc1375ecc30dad8ec59159ac1d,{},))):(jsx(Fragment,{},jsx(RadixThemesText,{as:"p",className:"empty-text"},"No custom stats added.")))))
  )
}


function Fragment_f58191500462d3a1751a52fc92c1bc40 () {
  const reflex___state____state__warframe_reflex___state____calculator_state = useContext(StateContexts.reflex___state____state__warframe_reflex___state____calculator_state)



  return (
    jsx(Fragment,{},(!((reflex___state____state__warframe_reflex___state____calculator_state.slot_selected_upgrades_rx_state_?.at?.(4)?.valueOf?.() === "Custom"?.valueOf?.()))?(jsx(Fragment,{},jsx(RadixThemesFlex,{align:"start",className:"rx-Stack",css:({ ["width"] : "100%", ["gap"] : "3" }),direction:"column",gap:"3"},jsx(RadixThemesGrid,{columns:"repeat(2, minmax(0, 1fr))",css:({ ["columnGap"] : "8px", ["width"] : "100%" })},jsx(RadixThemesFlex,{align:"start",className:"rx-Stack",css:({ ["gap"] : "1", ["width"] : "100%" }),direction:"column",gap:"3"},jsx(RadixThemesText,{as:"p",className:"field-label"},"Rank"),jsx(Debounceinput_46f02e3e5e046c9263eed21226c7ea85,{},)),jsx(Fragment_f85760e210f5d199c01edad38a532e41,{},)),jsx(Fragment_4fc28b488cfca806c00b948e30207280,{},),jsx(RadixThemesSeparator,{css:({ ["width"] : "100%" }),size:"4"},),jsx(Fragment_71466c6a68ba5e730b37606713a0a708,{},)))):(jsx(Fragment,{},jsx(RadixThemesFlex,{align:"start",className:"rx-Stack",css:({ ["width"] : "100%", ["gap"] : "3" }),direction:"column",gap:"3"},jsx(RadixThemesGrid,{columns:"minmax(0, 1fr) 32px",css:({ ["columnGap"] : "8px", ["width"] : "100%" })},jsx(Select__root_6c9a8276e83652a8820d8fe5231a164d,{},),jsx(Button_33a082992cac13dee44a490061b3524c,{},)),jsx(Fragment_4ea8bb53193dd301c5cfa443c6b6a03b,{},),jsx(RadixThemesSeparator,{css:({ ["width"] : "100%" }),size:"4"},),jsx(Fragment_71466c6a68ba5e730b37606713a0a708,{},))))))
  )
}


function Badge_648b7852ad11ffe7b4c434a5772a62e9 () {
  const reflex___state____state__warframe_reflex___state____calculator_state = useContext(StateContexts.reflex___state____state__warframe_reflex___state____calculator_state)



  return (
    jsx(RadixThemesBadge,{className:"contribution-badge",variant:"soft"},reflex___state____state__warframe_reflex___state____calculator_state.slot_contributions_rx_state_?.at?.(5))
  )
}


function Select__root_8c868c5b431b9090cd1ad0debe50a16f () {
  const reflex___state____state__warframe_reflex___state____calculator_state = useContext(StateContexts.reflex___state____state__warframe_reflex___state____calculator_state)
const [addEvents, connectErrors] = useContext(EventLoopContext);

const on_change_6df6b06ca73efd0e1a5caa623a5aa3fe = useCallback(((_ev_0) => (addEvents([(ReflexEvent("reflex___state____state.warframe_reflex___state____calculator_state.set_slot_upgrade", ({ ["index"] : 5, ["value"] : _ev_0 }), ({  })))], [_ev_0], ({  })))), [addEvents, ReflexEvent])

  return (
    jsx(RadixThemesSelect.Root,{onValueChange:on_change_6df6b06ca73efd0e1a5caa623a5aa3fe,value:reflex___state____state__warframe_reflex___state____calculator_state.slot_selected_upgrades_rx_state_?.at?.(5)},jsx(RadixThemesSelect.Trigger,{css:({ ["width"] : "100%" })},),jsx(RadixThemesSelect.Content,{position:"popper"},jsx(Select__group_a3ecac2495351b434ca1713de89fa7a8,{},)))
  )
}


function Debounceinput_6e3d0524cd794791a73326b59e7c495d () {
  const reflex___state____state__warframe_reflex___state____calculator_state = useContext(StateContexts.reflex___state____state__warframe_reflex___state____calculator_state)
const [addEvents, connectErrors] = useContext(EventLoopContext);

const on_change_44024a758b525fd022855eff478ce7df = useCallback(((_e) => (addEvents([(ReflexEvent("reflex___state____state.warframe_reflex___state____calculator_state.set_slot_rank", ({ ["index"] : 5, ["value"] : _e?.["target"]?.["value"] }), ({  })))], [_e], ({  })))), [addEvents, ReflexEvent])

  return (
    jsx(DebounceInput,{css:({ ["width"] : "100%", ["debounceTimeout"] : 250 }),debounceTimeout:250,element:RadixThemesTextField.Root,max:reflex___state____state__warframe_reflex___state____calculator_state.slot_max_ranks_rx_state_?.at?.(5),min:0,onChange:on_change_44024a758b525fd022855eff478ce7df,step:"1",type:"number",value:(isNotNullOrUndefined(reflex___state____state__warframe_reflex___state____calculator_state.slot_ranks_rx_state_?.at?.(5)) ? reflex___state____state__warframe_reflex___state____calculator_state.slot_ranks_rx_state_?.at?.(5) : "")},)
  )
}


function Debounceinput_2cb04c7ac5120d23d5f2f821e825de03 () {
  const reflex___state____state__warframe_reflex___state____calculator_state = useContext(StateContexts.reflex___state____state__warframe_reflex___state____calculator_state)
const [addEvents, connectErrors] = useContext(EventLoopContext);

const on_change_d9398518b28cfcfbccc64ff5a32daeea = useCallback(((_e) => (addEvents([(ReflexEvent("reflex___state____state.warframe_reflex___state____calculator_state.set_slot_stacks", ({ ["index"] : 5, ["value"] : _e?.["target"]?.["value"] }), ({  })))], [_e], ({  })))), [addEvents, ReflexEvent])

  return (
    jsx(DebounceInput,{css:({ ["width"] : "100%", ["debounceTimeout"] : 250 }),debounceTimeout:250,element:RadixThemesTextField.Root,max:reflex___state____state__warframe_reflex___state____calculator_state.slot_max_stacks_rx_state_?.at?.(5),min:0,onChange:on_change_d9398518b28cfcfbccc64ff5a32daeea,step:"1",type:"number",value:(isNotNullOrUndefined(reflex___state____state__warframe_reflex___state____calculator_state.slot_stacks_rx_state_?.at?.(5)) ? reflex___state____state__warframe_reflex___state____calculator_state.slot_stacks_rx_state_?.at?.(5) : "")},)
  )
}


function Fragment_b5502f87d54f857ae5c8e2251ea0a1b6 () {
  const reflex___state____state__warframe_reflex___state____calculator_state = useContext(StateContexts.reflex___state____state__warframe_reflex___state____calculator_state)



  return (
    jsx(Fragment,{},((reflex___state____state__warframe_reflex___state____calculator_state.slot_max_stacks_rx_state_?.at?.(5) > 0)?(jsx(Fragment,{},jsx(RadixThemesFlex,{align:"start",className:"rx-Stack",css:({ ["gap"] : "1", ["width"] : "100%" }),direction:"column",gap:"3"},jsx(RadixThemesText,{as:"p",className:"field-label"},"Stacks"),jsx(Debounceinput_2cb04c7ac5120d23d5f2f821e825de03,{},)))):(jsx(Fragment,{},))))
  )
}


function Checkbox_cdd250490d6ef9d5d6dc7c69cf57adfc () {
  const reflex___state____state__warframe_reflex___state____calculator_state = useContext(StateContexts.reflex___state____state__warframe_reflex___state____calculator_state)
const [addEvents, connectErrors] = useContext(EventLoopContext);

const on_change_64a5b35385ad97c6ce0516e54183d4fb = useCallback(((_ev_0) => (addEvents([(ReflexEvent("reflex___state____state.warframe_reflex___state____calculator_state.set_slot_condition", ({ ["index"] : 5, ["value"] : _ev_0 }), ({  })))], [_ev_0], ({  })))), [addEvents, ReflexEvent])

  return (
    jsx(RadixThemesCheckbox,{checked:reflex___state____state__warframe_reflex___state____calculator_state.slot_conditions_enabled_rx_state_?.at?.(5),className:"conditional-checkbox-control",onCheckedChange:on_change_64a5b35385ad97c6ce0516e54183d4fb,size:"2"},)
  )
}


function Text_bd6d56050341a7bfabf031291c5d2fbd () {
  const reflex___state____state__warframe_reflex___state____calculator_state = useContext(StateContexts.reflex___state____state__warframe_reflex___state____calculator_state)



  return (
    jsx(RadixThemesText,{as:"p",className:"conditional-checkbox-label"},"Enable conditional: ",reflex___state____state__warframe_reflex___state____calculator_state.slot_condition_labels_rx_state_?.at?.(5))
  )
}


function Fragment_9a622e7d986d60fa2a9e838259be1b12 () {
  const reflex___state____state__warframe_reflex___state____calculator_state = useContext(StateContexts.reflex___state____state__warframe_reflex___state____calculator_state)



  return (
    jsx(Fragment,{},(reflex___state____state__warframe_reflex___state____calculator_state.slot_has_conditionals_rx_state_?.at?.(5)?(jsx(Fragment,{},jsx(RadixThemesFlex,{align:"start",className:"rx-Stack conditional-checkbox-row",direction:"row",gap:"3"},jsx(RadixThemesText,{as:"label",size:"2"},jsx(RadixThemesFlex,{gap:"2"},jsx(Checkbox_cdd250490d6ef9d5d6dc7c69cf57adfc,{},),"")),jsx(Text_bd6d56050341a7bfabf031291c5d2fbd,{},)))):(jsx(Fragment,{},))))
  )
}


function Flex_e9b9dd7c0a32cc793c5756ccfcc146e9 () {
  const reflex___state____state__warframe_reflex___state____calculator_state = useContext(StateContexts.reflex___state____state__warframe_reflex___state____calculator_state)



  return (
    jsx(RadixThemesFlex,{align:"start",className:"rx-Stack",css:({ ["width"] : "100%", ["gap"] : "1" }),direction:"column",gap:"3"},Array.prototype.map.call(reflex___state____state__warframe_reflex___state____calculator_state.slot_stat_rows_rx_state_?.at?.(5) ?? [],((row_rx_state_,index_6f0cc146e9e04bdc4ed627113713c33a)=>(jsx(RadixThemesFlex,{align:"center",className:"rx-Stack",css:({ ["width"] : "100%" }),direction:"row",key:index_6f0cc146e9e04bdc4ed627113713c33a,gap:"3"},jsx(RadixThemesText,{as:"p",className:"preview-label"},row_rx_state_?.["label"]),jsx(RadixThemesFlex,{css:({ ["flex"] : 1, ["justifySelf"] : "stretch", ["alignSelf"] : "stretch" })},),jsx(RadixThemesText,{as:"p",className:"preview-value"},row_rx_state_?.["value"]))))))
  )
}


function Fragment_5d6537057efa2e2da9d15fbdf835a9c2 () {
  const reflex___state____state__warframe_reflex___state____calculator_state = useContext(StateContexts.reflex___state____state__warframe_reflex___state____calculator_state)



  return (
    jsx(Fragment,{},((reflex___state____state__warframe_reflex___state____calculator_state.slot_stat_rows_rx_state_?.at?.(5).length > 0)?(jsx(Fragment,{},jsx(Flex_e9b9dd7c0a32cc793c5756ccfcc146e9,{},))):(jsx(Fragment,{},jsx(RadixThemesText,{as:"p",className:"empty-text"},"No stats.")))))
  )
}


function Select__group_b7362fcc9d22f0bab0a13f9b4c7cf61d () {
  const reflex___state____state__warframe_reflex___state____calculator_state = useContext(StateContexts.reflex___state____state__warframe_reflex___state____calculator_state)



  return (
    jsx(RadixThemesSelect.Group,{},"",Array.prototype.map.call(reflex___state____state__warframe_reflex___state____calculator_state.slot_available_fields_rx_state_?.at?.(5) ?? [],((item_rx_state_,index_d6d6157c99650830f12a866606ea87b7)=>(jsx(RadixThemesSelect.Item,{key:index_d6d6157c99650830f12a866606ea87b7,value:item_rx_state_},item_rx_state_)))))
  )
}


function Select__root_877c799b63cd788d74c4443097ce3113 () {
  const reflex___state____state__warframe_reflex___state____calculator_state = useContext(StateContexts.reflex___state____state__warframe_reflex___state____calculator_state)
const [addEvents, connectErrors] = useContext(EventLoopContext);

const on_change_2c013d1fea33ce189ae741a583a15b47 = useCallback(((_ev_0) => (addEvents([(ReflexEvent("reflex___state____state.warframe_reflex___state____calculator_state.set_slot_pending_field", ({ ["index"] : 5, ["value"] : _ev_0 }), ({  })))], [_ev_0], ({  })))), [addEvents, ReflexEvent])

  return (
    jsx(RadixThemesSelect.Root,{disabled:(reflex___state____state__warframe_reflex___state____calculator_state.slot_available_fields_rx_state_?.at?.(5).length?.valueOf?.() === 0?.valueOf?.()),onValueChange:on_change_2c013d1fea33ce189ae741a583a15b47,value:reflex___state____state__warframe_reflex___state____calculator_state.slot_pending_fields_rx_state_?.at?.(5)},jsx(RadixThemesSelect.Trigger,{css:({ ["width"] : "100%" })},),jsx(RadixThemesSelect.Content,{position:"popper"},jsx(Select__group_b7362fcc9d22f0bab0a13f9b4c7cf61d,{},)))
  )
}


function Button_0c3dc91d925c63744823d10e485416b5 () {
  const reflex___state____state__warframe_reflex___state____calculator_state = useContext(StateContexts.reflex___state____state__warframe_reflex___state____calculator_state)
const [addEvents, connectErrors] = useContext(EventLoopContext);

const on_click_f5bb7264b21fde90c2c7e00979b4e297 = useCallback(((_e) => (addEvents([(ReflexEvent("reflex___state____state.warframe_reflex___state____calculator_state.add_slot_field", ({ ["index"] : 5 }), ({  })))], [_e], ({  })))), [addEvents, ReflexEvent])

  return (
    jsx(RadixThemesButton,{className:"icon-button field-action-button",disabled:(reflex___state____state__warframe_reflex___state____calculator_state.slot_available_fields_rx_state_?.at?.(5).length?.valueOf?.() === 0?.valueOf?.()),onClick:on_click_f5bb7264b21fde90c2c7e00979b4e297},"+")
  )
}


function Flex_ee7ab1bdeb9aded1a060d068fed6f4d2 () {
  const reflex___state____state__warframe_reflex___state____calculator_state = useContext(StateContexts.reflex___state____state__warframe_reflex___state____calculator_state)
const [addEvents, connectErrors] = useContext(EventLoopContext);



  return (
    jsx(RadixThemesFlex,{align:"start",className:"rx-Stack",css:({ ["width"] : "100%", ["gap"] : "2" }),direction:"column",gap:"3"},Array.prototype.map.call(reflex___state____state__warframe_reflex___state____calculator_state.slot_fields_rx_state_?.at?.(5) ?? [],((field_rx_state_,index_ad9d7b81e0e65a5948a3885101cbe585)=>(jsx(RadixThemesGrid,{align:"center",columns:"84px minmax(0, 1fr) 32px",css:({ ["columnGap"] : "8px", ["width"] : "100%" }),key:index_ad9d7b81e0e65a5948a3885101cbe585},jsx(RadixThemesText,{as:"p",className:"compact-label"},field_rx_state_?.["label"]),jsx(DebounceInput,{css:({ ["debounceTimeout"] : 250, ["width"] : "100%" }),debounceTimeout:250,element:RadixThemesTextField.Root,max:field_rx_state_?.["max_value"],min:field_rx_state_?.["min_value"],onChange:((_e) => (addEvents([(ReflexEvent("reflex___state____state.warframe_reflex___state____calculator_state.set_slot_field_value", ({ ["index"] : 5, ["field_name"] : field_rx_state_?.["name"], ["value"] : _e?.["target"]?.["value"] }), ({  })))], [_e], ({  })))),step:(field_rx_state_?.["integer"] ? "1" : "0.001"),type:"number",value:(isNotNullOrUndefined(field_rx_state_?.["value"]) ? field_rx_state_?.["value"] : "")},),jsx(RadixThemesButton,{className:"icon-button field-action-button",onClick:((_e) => (addEvents([(ReflexEvent("reflex___state____state.warframe_reflex___state____calculator_state.remove_slot_field", ({ ["index"] : 5, ["field_name"] : field_rx_state_?.["name"] }), ({  })))], [_e], ({  })))),variant:"soft"},"\u00d7"))))))
  )
}


function Fragment_0f542837bc646d146e6c25204d9b94d7 () {
  const reflex___state____state__warframe_reflex___state____calculator_state = useContext(StateContexts.reflex___state____state__warframe_reflex___state____calculator_state)



  return (
    jsx(Fragment,{},((reflex___state____state__warframe_reflex___state____calculator_state.slot_fields_rx_state_?.at?.(5).length > 0)?(jsx(Fragment,{},jsx(Flex_ee7ab1bdeb9aded1a060d068fed6f4d2,{},))):(jsx(Fragment,{},jsx(RadixThemesText,{as:"p",className:"empty-text"},"No custom stats added.")))))
  )
}


function Fragment_4bbd69e76ede1f24b898d40810c0f05b () {
  const reflex___state____state__warframe_reflex___state____calculator_state = useContext(StateContexts.reflex___state____state__warframe_reflex___state____calculator_state)



  return (
    jsx(Fragment,{},(!((reflex___state____state__warframe_reflex___state____calculator_state.slot_selected_upgrades_rx_state_?.at?.(5)?.valueOf?.() === "Custom"?.valueOf?.()))?(jsx(Fragment,{},jsx(RadixThemesFlex,{align:"start",className:"rx-Stack",css:({ ["width"] : "100%", ["gap"] : "3" }),direction:"column",gap:"3"},jsx(RadixThemesGrid,{columns:"repeat(2, minmax(0, 1fr))",css:({ ["columnGap"] : "8px", ["width"] : "100%" })},jsx(RadixThemesFlex,{align:"start",className:"rx-Stack",css:({ ["gap"] : "1", ["width"] : "100%" }),direction:"column",gap:"3"},jsx(RadixThemesText,{as:"p",className:"field-label"},"Rank"),jsx(Debounceinput_6e3d0524cd794791a73326b59e7c495d,{},)),jsx(Fragment_b5502f87d54f857ae5c8e2251ea0a1b6,{},)),jsx(Fragment_9a622e7d986d60fa2a9e838259be1b12,{},),jsx(RadixThemesSeparator,{css:({ ["width"] : "100%" }),size:"4"},),jsx(Fragment_5d6537057efa2e2da9d15fbdf835a9c2,{},)))):(jsx(Fragment,{},jsx(RadixThemesFlex,{align:"start",className:"rx-Stack",css:({ ["width"] : "100%", ["gap"] : "3" }),direction:"column",gap:"3"},jsx(RadixThemesGrid,{columns:"minmax(0, 1fr) 32px",css:({ ["columnGap"] : "8px", ["width"] : "100%" })},jsx(Select__root_877c799b63cd788d74c4443097ce3113,{},),jsx(Button_0c3dc91d925c63744823d10e485416b5,{},)),jsx(Fragment_0f542837bc646d146e6c25204d9b94d7,{},),jsx(RadixThemesSeparator,{css:({ ["width"] : "100%" }),size:"4"},),jsx(Fragment_5d6537057efa2e2da9d15fbdf835a9c2,{},))))))
  )
}


function Badge_43191d40e80b8bba12520da6d407d0db () {
  const reflex___state____state__warframe_reflex___state____calculator_state = useContext(StateContexts.reflex___state____state__warframe_reflex___state____calculator_state)



  return (
    jsx(RadixThemesBadge,{className:"contribution-badge",variant:"soft"},reflex___state____state__warframe_reflex___state____calculator_state.slot_contributions_rx_state_?.at?.(6))
  )
}


function Select__root_607090528477ce11ec5b96c796fb1e89 () {
  const reflex___state____state__warframe_reflex___state____calculator_state = useContext(StateContexts.reflex___state____state__warframe_reflex___state____calculator_state)
const [addEvents, connectErrors] = useContext(EventLoopContext);

const on_change_9599418165d3e87805b7381539cc6071 = useCallback(((_ev_0) => (addEvents([(ReflexEvent("reflex___state____state.warframe_reflex___state____calculator_state.set_slot_upgrade", ({ ["index"] : 6, ["value"] : _ev_0 }), ({  })))], [_ev_0], ({  })))), [addEvents, ReflexEvent])

  return (
    jsx(RadixThemesSelect.Root,{onValueChange:on_change_9599418165d3e87805b7381539cc6071,value:reflex___state____state__warframe_reflex___state____calculator_state.slot_selected_upgrades_rx_state_?.at?.(6)},jsx(RadixThemesSelect.Trigger,{css:({ ["width"] : "100%" })},),jsx(RadixThemesSelect.Content,{position:"popper"},jsx(Select__group_a3ecac2495351b434ca1713de89fa7a8,{},)))
  )
}


function Debounceinput_08777da2dca71da73a4f951b95ace7b0 () {
  const reflex___state____state__warframe_reflex___state____calculator_state = useContext(StateContexts.reflex___state____state__warframe_reflex___state____calculator_state)
const [addEvents, connectErrors] = useContext(EventLoopContext);

const on_change_1b538dcc9e31b566dadfaf1347c93ac7 = useCallback(((_e) => (addEvents([(ReflexEvent("reflex___state____state.warframe_reflex___state____calculator_state.set_slot_rank", ({ ["index"] : 6, ["value"] : _e?.["target"]?.["value"] }), ({  })))], [_e], ({  })))), [addEvents, ReflexEvent])

  return (
    jsx(DebounceInput,{css:({ ["width"] : "100%", ["debounceTimeout"] : 250 }),debounceTimeout:250,element:RadixThemesTextField.Root,max:reflex___state____state__warframe_reflex___state____calculator_state.slot_max_ranks_rx_state_?.at?.(6),min:0,onChange:on_change_1b538dcc9e31b566dadfaf1347c93ac7,step:"1",type:"number",value:(isNotNullOrUndefined(reflex___state____state__warframe_reflex___state____calculator_state.slot_ranks_rx_state_?.at?.(6)) ? reflex___state____state__warframe_reflex___state____calculator_state.slot_ranks_rx_state_?.at?.(6) : "")},)
  )
}


function Debounceinput_9ee5040ef28c1323c0d154d20958377b () {
  const reflex___state____state__warframe_reflex___state____calculator_state = useContext(StateContexts.reflex___state____state__warframe_reflex___state____calculator_state)
const [addEvents, connectErrors] = useContext(EventLoopContext);

const on_change_a3d0a1ce114fcd13611886ac439f3ce6 = useCallback(((_e) => (addEvents([(ReflexEvent("reflex___state____state.warframe_reflex___state____calculator_state.set_slot_stacks", ({ ["index"] : 6, ["value"] : _e?.["target"]?.["value"] }), ({  })))], [_e], ({  })))), [addEvents, ReflexEvent])

  return (
    jsx(DebounceInput,{css:({ ["width"] : "100%", ["debounceTimeout"] : 250 }),debounceTimeout:250,element:RadixThemesTextField.Root,max:reflex___state____state__warframe_reflex___state____calculator_state.slot_max_stacks_rx_state_?.at?.(6),min:0,onChange:on_change_a3d0a1ce114fcd13611886ac439f3ce6,step:"1",type:"number",value:(isNotNullOrUndefined(reflex___state____state__warframe_reflex___state____calculator_state.slot_stacks_rx_state_?.at?.(6)) ? reflex___state____state__warframe_reflex___state____calculator_state.slot_stacks_rx_state_?.at?.(6) : "")},)
  )
}


function Fragment_ca3e2ddd21248666f13d33ab002fe94b () {
  const reflex___state____state__warframe_reflex___state____calculator_state = useContext(StateContexts.reflex___state____state__warframe_reflex___state____calculator_state)



  return (
    jsx(Fragment,{},((reflex___state____state__warframe_reflex___state____calculator_state.slot_max_stacks_rx_state_?.at?.(6) > 0)?(jsx(Fragment,{},jsx(RadixThemesFlex,{align:"start",className:"rx-Stack",css:({ ["gap"] : "1", ["width"] : "100%" }),direction:"column",gap:"3"},jsx(RadixThemesText,{as:"p",className:"field-label"},"Stacks"),jsx(Debounceinput_9ee5040ef28c1323c0d154d20958377b,{},)))):(jsx(Fragment,{},))))
  )
}


function Checkbox_6416872c7f05fb943067f27d6589b950 () {
  const reflex___state____state__warframe_reflex___state____calculator_state = useContext(StateContexts.reflex___state____state__warframe_reflex___state____calculator_state)
const [addEvents, connectErrors] = useContext(EventLoopContext);

const on_change_fea33b0d1f492bb933e8bf2bb377ffe3 = useCallback(((_ev_0) => (addEvents([(ReflexEvent("reflex___state____state.warframe_reflex___state____calculator_state.set_slot_condition", ({ ["index"] : 6, ["value"] : _ev_0 }), ({  })))], [_ev_0], ({  })))), [addEvents, ReflexEvent])

  return (
    jsx(RadixThemesCheckbox,{checked:reflex___state____state__warframe_reflex___state____calculator_state.slot_conditions_enabled_rx_state_?.at?.(6),className:"conditional-checkbox-control",onCheckedChange:on_change_fea33b0d1f492bb933e8bf2bb377ffe3,size:"2"},)
  )
}


function Text_4c9496fdf9a3ab7614eaf3167ad40726 () {
  const reflex___state____state__warframe_reflex___state____calculator_state = useContext(StateContexts.reflex___state____state__warframe_reflex___state____calculator_state)



  return (
    jsx(RadixThemesText,{as:"p",className:"conditional-checkbox-label"},"Enable conditional: ",reflex___state____state__warframe_reflex___state____calculator_state.slot_condition_labels_rx_state_?.at?.(6))
  )
}


function Fragment_ec35430df3692ffa03b2bf57ff720686 () {
  const reflex___state____state__warframe_reflex___state____calculator_state = useContext(StateContexts.reflex___state____state__warframe_reflex___state____calculator_state)



  return (
    jsx(Fragment,{},(reflex___state____state__warframe_reflex___state____calculator_state.slot_has_conditionals_rx_state_?.at?.(6)?(jsx(Fragment,{},jsx(RadixThemesFlex,{align:"start",className:"rx-Stack conditional-checkbox-row",direction:"row",gap:"3"},jsx(RadixThemesText,{as:"label",size:"2"},jsx(RadixThemesFlex,{gap:"2"},jsx(Checkbox_6416872c7f05fb943067f27d6589b950,{},),"")),jsx(Text_4c9496fdf9a3ab7614eaf3167ad40726,{},)))):(jsx(Fragment,{},))))
  )
}


function Flex_64ade4a24f0cc22fb9df5344c51f865b () {
  const reflex___state____state__warframe_reflex___state____calculator_state = useContext(StateContexts.reflex___state____state__warframe_reflex___state____calculator_state)



  return (
    jsx(RadixThemesFlex,{align:"start",className:"rx-Stack",css:({ ["width"] : "100%", ["gap"] : "1" }),direction:"column",gap:"3"},Array.prototype.map.call(reflex___state____state__warframe_reflex___state____calculator_state.slot_stat_rows_rx_state_?.at?.(6) ?? [],((row_rx_state_,index_6f0cc146e9e04bdc4ed627113713c33a)=>(jsx(RadixThemesFlex,{align:"center",className:"rx-Stack",css:({ ["width"] : "100%" }),direction:"row",key:index_6f0cc146e9e04bdc4ed627113713c33a,gap:"3"},jsx(RadixThemesText,{as:"p",className:"preview-label"},row_rx_state_?.["label"]),jsx(RadixThemesFlex,{css:({ ["flex"] : 1, ["justifySelf"] : "stretch", ["alignSelf"] : "stretch" })},),jsx(RadixThemesText,{as:"p",className:"preview-value"},row_rx_state_?.["value"]))))))
  )
}


function Fragment_d28f023b6b769568f64ab0ff19b35d58 () {
  const reflex___state____state__warframe_reflex___state____calculator_state = useContext(StateContexts.reflex___state____state__warframe_reflex___state____calculator_state)



  return (
    jsx(Fragment,{},((reflex___state____state__warframe_reflex___state____calculator_state.slot_stat_rows_rx_state_?.at?.(6).length > 0)?(jsx(Fragment,{},jsx(Flex_64ade4a24f0cc22fb9df5344c51f865b,{},))):(jsx(Fragment,{},jsx(RadixThemesText,{as:"p",className:"empty-text"},"No stats.")))))
  )
}


function Select__group_fcf4232ed5b969fb564cab224a8c000f () {
  const reflex___state____state__warframe_reflex___state____calculator_state = useContext(StateContexts.reflex___state____state__warframe_reflex___state____calculator_state)



  return (
    jsx(RadixThemesSelect.Group,{},"",Array.prototype.map.call(reflex___state____state__warframe_reflex___state____calculator_state.slot_available_fields_rx_state_?.at?.(6) ?? [],((item_rx_state_,index_d6d6157c99650830f12a866606ea87b7)=>(jsx(RadixThemesSelect.Item,{key:index_d6d6157c99650830f12a866606ea87b7,value:item_rx_state_},item_rx_state_)))))
  )
}


function Select__root_74990220da9da04aedd51be3efa09bab () {
  const reflex___state____state__warframe_reflex___state____calculator_state = useContext(StateContexts.reflex___state____state__warframe_reflex___state____calculator_state)
const [addEvents, connectErrors] = useContext(EventLoopContext);

const on_change_a58de2bb1d0dd60c5ae10df9a88385a1 = useCallback(((_ev_0) => (addEvents([(ReflexEvent("reflex___state____state.warframe_reflex___state____calculator_state.set_slot_pending_field", ({ ["index"] : 6, ["value"] : _ev_0 }), ({  })))], [_ev_0], ({  })))), [addEvents, ReflexEvent])

  return (
    jsx(RadixThemesSelect.Root,{disabled:(reflex___state____state__warframe_reflex___state____calculator_state.slot_available_fields_rx_state_?.at?.(6).length?.valueOf?.() === 0?.valueOf?.()),onValueChange:on_change_a58de2bb1d0dd60c5ae10df9a88385a1,value:reflex___state____state__warframe_reflex___state____calculator_state.slot_pending_fields_rx_state_?.at?.(6)},jsx(RadixThemesSelect.Trigger,{css:({ ["width"] : "100%" })},),jsx(RadixThemesSelect.Content,{position:"popper"},jsx(Select__group_fcf4232ed5b969fb564cab224a8c000f,{},)))
  )
}


function Button_b98049794af1290c630f1eaba4c5998c () {
  const reflex___state____state__warframe_reflex___state____calculator_state = useContext(StateContexts.reflex___state____state__warframe_reflex___state____calculator_state)
const [addEvents, connectErrors] = useContext(EventLoopContext);

const on_click_29dfbc14160ac73f4d7b9843e758da48 = useCallback(((_e) => (addEvents([(ReflexEvent("reflex___state____state.warframe_reflex___state____calculator_state.add_slot_field", ({ ["index"] : 6 }), ({  })))], [_e], ({  })))), [addEvents, ReflexEvent])

  return (
    jsx(RadixThemesButton,{className:"icon-button field-action-button",disabled:(reflex___state____state__warframe_reflex___state____calculator_state.slot_available_fields_rx_state_?.at?.(6).length?.valueOf?.() === 0?.valueOf?.()),onClick:on_click_29dfbc14160ac73f4d7b9843e758da48},"+")
  )
}


function Flex_d41f20a39aab7690146d3cdc09c41320 () {
  const reflex___state____state__warframe_reflex___state____calculator_state = useContext(StateContexts.reflex___state____state__warframe_reflex___state____calculator_state)
const [addEvents, connectErrors] = useContext(EventLoopContext);



  return (
    jsx(RadixThemesFlex,{align:"start",className:"rx-Stack",css:({ ["width"] : "100%", ["gap"] : "2" }),direction:"column",gap:"3"},Array.prototype.map.call(reflex___state____state__warframe_reflex___state____calculator_state.slot_fields_rx_state_?.at?.(6) ?? [],((field_rx_state_,index_ad9d7b81e0e65a5948a3885101cbe585)=>(jsx(RadixThemesGrid,{align:"center",columns:"84px minmax(0, 1fr) 32px",css:({ ["columnGap"] : "8px", ["width"] : "100%" }),key:index_ad9d7b81e0e65a5948a3885101cbe585},jsx(RadixThemesText,{as:"p",className:"compact-label"},field_rx_state_?.["label"]),jsx(DebounceInput,{css:({ ["debounceTimeout"] : 250, ["width"] : "100%" }),debounceTimeout:250,element:RadixThemesTextField.Root,max:field_rx_state_?.["max_value"],min:field_rx_state_?.["min_value"],onChange:((_e) => (addEvents([(ReflexEvent("reflex___state____state.warframe_reflex___state____calculator_state.set_slot_field_value", ({ ["index"] : 6, ["field_name"] : field_rx_state_?.["name"], ["value"] : _e?.["target"]?.["value"] }), ({  })))], [_e], ({  })))),step:(field_rx_state_?.["integer"] ? "1" : "0.001"),type:"number",value:(isNotNullOrUndefined(field_rx_state_?.["value"]) ? field_rx_state_?.["value"] : "")},),jsx(RadixThemesButton,{className:"icon-button field-action-button",onClick:((_e) => (addEvents([(ReflexEvent("reflex___state____state.warframe_reflex___state____calculator_state.remove_slot_field", ({ ["index"] : 6, ["field_name"] : field_rx_state_?.["name"] }), ({  })))], [_e], ({  })))),variant:"soft"},"\u00d7"))))))
  )
}


function Fragment_5d2052fc6e1e10b91f195cb02ab94602 () {
  const reflex___state____state__warframe_reflex___state____calculator_state = useContext(StateContexts.reflex___state____state__warframe_reflex___state____calculator_state)



  return (
    jsx(Fragment,{},((reflex___state____state__warframe_reflex___state____calculator_state.slot_fields_rx_state_?.at?.(6).length > 0)?(jsx(Fragment,{},jsx(Flex_d41f20a39aab7690146d3cdc09c41320,{},))):(jsx(Fragment,{},jsx(RadixThemesText,{as:"p",className:"empty-text"},"No custom stats added.")))))
  )
}


function Fragment_da9cbea26663da96f0112422bb6c7c66 () {
  const reflex___state____state__warframe_reflex___state____calculator_state = useContext(StateContexts.reflex___state____state__warframe_reflex___state____calculator_state)



  return (
    jsx(Fragment,{},(!((reflex___state____state__warframe_reflex___state____calculator_state.slot_selected_upgrades_rx_state_?.at?.(6)?.valueOf?.() === "Custom"?.valueOf?.()))?(jsx(Fragment,{},jsx(RadixThemesFlex,{align:"start",className:"rx-Stack",css:({ ["width"] : "100%", ["gap"] : "3" }),direction:"column",gap:"3"},jsx(RadixThemesGrid,{columns:"repeat(2, minmax(0, 1fr))",css:({ ["columnGap"] : "8px", ["width"] : "100%" })},jsx(RadixThemesFlex,{align:"start",className:"rx-Stack",css:({ ["gap"] : "1", ["width"] : "100%" }),direction:"column",gap:"3"},jsx(RadixThemesText,{as:"p",className:"field-label"},"Rank"),jsx(Debounceinput_08777da2dca71da73a4f951b95ace7b0,{},)),jsx(Fragment_ca3e2ddd21248666f13d33ab002fe94b,{},)),jsx(Fragment_ec35430df3692ffa03b2bf57ff720686,{},),jsx(RadixThemesSeparator,{css:({ ["width"] : "100%" }),size:"4"},),jsx(Fragment_d28f023b6b769568f64ab0ff19b35d58,{},)))):(jsx(Fragment,{},jsx(RadixThemesFlex,{align:"start",className:"rx-Stack",css:({ ["width"] : "100%", ["gap"] : "3" }),direction:"column",gap:"3"},jsx(RadixThemesGrid,{columns:"minmax(0, 1fr) 32px",css:({ ["columnGap"] : "8px", ["width"] : "100%" })},jsx(Select__root_74990220da9da04aedd51be3efa09bab,{},),jsx(Button_b98049794af1290c630f1eaba4c5998c,{},)),jsx(Fragment_5d2052fc6e1e10b91f195cb02ab94602,{},),jsx(RadixThemesSeparator,{css:({ ["width"] : "100%" }),size:"4"},),jsx(Fragment_d28f023b6b769568f64ab0ff19b35d58,{},))))))
  )
}


function Badge_de4494a6811cc0c45c6d23690da1c4bc () {
  const reflex___state____state__warframe_reflex___state____calculator_state = useContext(StateContexts.reflex___state____state__warframe_reflex___state____calculator_state)



  return (
    jsx(RadixThemesBadge,{className:"contribution-badge",variant:"soft"},reflex___state____state__warframe_reflex___state____calculator_state.slot_contributions_rx_state_?.at?.(7))
  )
}


function Select__root_363ac76ac3fac0b169b905524d5a092d () {
  const reflex___state____state__warframe_reflex___state____calculator_state = useContext(StateContexts.reflex___state____state__warframe_reflex___state____calculator_state)
const [addEvents, connectErrors] = useContext(EventLoopContext);

const on_change_c8f27f59ba2a34cc337cb6c20ee85d64 = useCallback(((_ev_0) => (addEvents([(ReflexEvent("reflex___state____state.warframe_reflex___state____calculator_state.set_slot_upgrade", ({ ["index"] : 7, ["value"] : _ev_0 }), ({  })))], [_ev_0], ({  })))), [addEvents, ReflexEvent])

  return (
    jsx(RadixThemesSelect.Root,{onValueChange:on_change_c8f27f59ba2a34cc337cb6c20ee85d64,value:reflex___state____state__warframe_reflex___state____calculator_state.slot_selected_upgrades_rx_state_?.at?.(7)},jsx(RadixThemesSelect.Trigger,{css:({ ["width"] : "100%" })},),jsx(RadixThemesSelect.Content,{position:"popper"},jsx(Select__group_a3ecac2495351b434ca1713de89fa7a8,{},)))
  )
}


function Debounceinput_65044447264598cd6e3d467977a9e84a () {
  const reflex___state____state__warframe_reflex___state____calculator_state = useContext(StateContexts.reflex___state____state__warframe_reflex___state____calculator_state)
const [addEvents, connectErrors] = useContext(EventLoopContext);

const on_change_0264ffb804616b24d3d233b5afdda74b = useCallback(((_e) => (addEvents([(ReflexEvent("reflex___state____state.warframe_reflex___state____calculator_state.set_slot_rank", ({ ["index"] : 7, ["value"] : _e?.["target"]?.["value"] }), ({  })))], [_e], ({  })))), [addEvents, ReflexEvent])

  return (
    jsx(DebounceInput,{css:({ ["width"] : "100%", ["debounceTimeout"] : 250 }),debounceTimeout:250,element:RadixThemesTextField.Root,max:reflex___state____state__warframe_reflex___state____calculator_state.slot_max_ranks_rx_state_?.at?.(7),min:0,onChange:on_change_0264ffb804616b24d3d233b5afdda74b,step:"1",type:"number",value:(isNotNullOrUndefined(reflex___state____state__warframe_reflex___state____calculator_state.slot_ranks_rx_state_?.at?.(7)) ? reflex___state____state__warframe_reflex___state____calculator_state.slot_ranks_rx_state_?.at?.(7) : "")},)
  )
}


function Debounceinput_9a1499e60f2094e81059c30a0a975049 () {
  const reflex___state____state__warframe_reflex___state____calculator_state = useContext(StateContexts.reflex___state____state__warframe_reflex___state____calculator_state)
const [addEvents, connectErrors] = useContext(EventLoopContext);

const on_change_4b3ab43bd723502240273cdab87bd39b = useCallback(((_e) => (addEvents([(ReflexEvent("reflex___state____state.warframe_reflex___state____calculator_state.set_slot_stacks", ({ ["index"] : 7, ["value"] : _e?.["target"]?.["value"] }), ({  })))], [_e], ({  })))), [addEvents, ReflexEvent])

  return (
    jsx(DebounceInput,{css:({ ["width"] : "100%", ["debounceTimeout"] : 250 }),debounceTimeout:250,element:RadixThemesTextField.Root,max:reflex___state____state__warframe_reflex___state____calculator_state.slot_max_stacks_rx_state_?.at?.(7),min:0,onChange:on_change_4b3ab43bd723502240273cdab87bd39b,step:"1",type:"number",value:(isNotNullOrUndefined(reflex___state____state__warframe_reflex___state____calculator_state.slot_stacks_rx_state_?.at?.(7)) ? reflex___state____state__warframe_reflex___state____calculator_state.slot_stacks_rx_state_?.at?.(7) : "")},)
  )
}


function Fragment_7757b9e9d1bee5d3aa8e128fd17e19a2 () {
  const reflex___state____state__warframe_reflex___state____calculator_state = useContext(StateContexts.reflex___state____state__warframe_reflex___state____calculator_state)



  return (
    jsx(Fragment,{},((reflex___state____state__warframe_reflex___state____calculator_state.slot_max_stacks_rx_state_?.at?.(7) > 0)?(jsx(Fragment,{},jsx(RadixThemesFlex,{align:"start",className:"rx-Stack",css:({ ["gap"] : "1", ["width"] : "100%" }),direction:"column",gap:"3"},jsx(RadixThemesText,{as:"p",className:"field-label"},"Stacks"),jsx(Debounceinput_9a1499e60f2094e81059c30a0a975049,{},)))):(jsx(Fragment,{},))))
  )
}


function Checkbox_213ee3b4f1a2795476947c0c2f76bcff () {
  const reflex___state____state__warframe_reflex___state____calculator_state = useContext(StateContexts.reflex___state____state__warframe_reflex___state____calculator_state)
const [addEvents, connectErrors] = useContext(EventLoopContext);

const on_change_a245f2117bbf9cf298fa02a570398ec7 = useCallback(((_ev_0) => (addEvents([(ReflexEvent("reflex___state____state.warframe_reflex___state____calculator_state.set_slot_condition", ({ ["index"] : 7, ["value"] : _ev_0 }), ({  })))], [_ev_0], ({  })))), [addEvents, ReflexEvent])

  return (
    jsx(RadixThemesCheckbox,{checked:reflex___state____state__warframe_reflex___state____calculator_state.slot_conditions_enabled_rx_state_?.at?.(7),className:"conditional-checkbox-control",onCheckedChange:on_change_a245f2117bbf9cf298fa02a570398ec7,size:"2"},)
  )
}


function Text_03d99ba445caaeff7e49bd1ea6976fe9 () {
  const reflex___state____state__warframe_reflex___state____calculator_state = useContext(StateContexts.reflex___state____state__warframe_reflex___state____calculator_state)



  return (
    jsx(RadixThemesText,{as:"p",className:"conditional-checkbox-label"},"Enable conditional: ",reflex___state____state__warframe_reflex___state____calculator_state.slot_condition_labels_rx_state_?.at?.(7))
  )
}


function Fragment_2ac953744385db7adf9339ba188c0049 () {
  const reflex___state____state__warframe_reflex___state____calculator_state = useContext(StateContexts.reflex___state____state__warframe_reflex___state____calculator_state)



  return (
    jsx(Fragment,{},(reflex___state____state__warframe_reflex___state____calculator_state.slot_has_conditionals_rx_state_?.at?.(7)?(jsx(Fragment,{},jsx(RadixThemesFlex,{align:"start",className:"rx-Stack conditional-checkbox-row",direction:"row",gap:"3"},jsx(RadixThemesText,{as:"label",size:"2"},jsx(RadixThemesFlex,{gap:"2"},jsx(Checkbox_213ee3b4f1a2795476947c0c2f76bcff,{},),"")),jsx(Text_03d99ba445caaeff7e49bd1ea6976fe9,{},)))):(jsx(Fragment,{},))))
  )
}


function Flex_8137917c9fdf96358487e75fe6caeb57 () {
  const reflex___state____state__warframe_reflex___state____calculator_state = useContext(StateContexts.reflex___state____state__warframe_reflex___state____calculator_state)



  return (
    jsx(RadixThemesFlex,{align:"start",className:"rx-Stack",css:({ ["width"] : "100%", ["gap"] : "1" }),direction:"column",gap:"3"},Array.prototype.map.call(reflex___state____state__warframe_reflex___state____calculator_state.slot_stat_rows_rx_state_?.at?.(7) ?? [],((row_rx_state_,index_6f0cc146e9e04bdc4ed627113713c33a)=>(jsx(RadixThemesFlex,{align:"center",className:"rx-Stack",css:({ ["width"] : "100%" }),direction:"row",key:index_6f0cc146e9e04bdc4ed627113713c33a,gap:"3"},jsx(RadixThemesText,{as:"p",className:"preview-label"},row_rx_state_?.["label"]),jsx(RadixThemesFlex,{css:({ ["flex"] : 1, ["justifySelf"] : "stretch", ["alignSelf"] : "stretch" })},),jsx(RadixThemesText,{as:"p",className:"preview-value"},row_rx_state_?.["value"]))))))
  )
}


function Fragment_727d0e4b29d62e947bd26ccac3fcbc69 () {
  const reflex___state____state__warframe_reflex___state____calculator_state = useContext(StateContexts.reflex___state____state__warframe_reflex___state____calculator_state)



  return (
    jsx(Fragment,{},((reflex___state____state__warframe_reflex___state____calculator_state.slot_stat_rows_rx_state_?.at?.(7).length > 0)?(jsx(Fragment,{},jsx(Flex_8137917c9fdf96358487e75fe6caeb57,{},))):(jsx(Fragment,{},jsx(RadixThemesText,{as:"p",className:"empty-text"},"No stats.")))))
  )
}


function Select__group_da859e5be41a722f6cd81ea69baaf2ac () {
  const reflex___state____state__warframe_reflex___state____calculator_state = useContext(StateContexts.reflex___state____state__warframe_reflex___state____calculator_state)



  return (
    jsx(RadixThemesSelect.Group,{},"",Array.prototype.map.call(reflex___state____state__warframe_reflex___state____calculator_state.slot_available_fields_rx_state_?.at?.(7) ?? [],((item_rx_state_,index_d6d6157c99650830f12a866606ea87b7)=>(jsx(RadixThemesSelect.Item,{key:index_d6d6157c99650830f12a866606ea87b7,value:item_rx_state_},item_rx_state_)))))
  )
}


function Select__root_e687dd8ba6a833296c4ba574907b04e5 () {
  const reflex___state____state__warframe_reflex___state____calculator_state = useContext(StateContexts.reflex___state____state__warframe_reflex___state____calculator_state)
const [addEvents, connectErrors] = useContext(EventLoopContext);

const on_change_60a6159dfc77a90993c44ee39589211d = useCallback(((_ev_0) => (addEvents([(ReflexEvent("reflex___state____state.warframe_reflex___state____calculator_state.set_slot_pending_field", ({ ["index"] : 7, ["value"] : _ev_0 }), ({  })))], [_ev_0], ({  })))), [addEvents, ReflexEvent])

  return (
    jsx(RadixThemesSelect.Root,{disabled:(reflex___state____state__warframe_reflex___state____calculator_state.slot_available_fields_rx_state_?.at?.(7).length?.valueOf?.() === 0?.valueOf?.()),onValueChange:on_change_60a6159dfc77a90993c44ee39589211d,value:reflex___state____state__warframe_reflex___state____calculator_state.slot_pending_fields_rx_state_?.at?.(7)},jsx(RadixThemesSelect.Trigger,{css:({ ["width"] : "100%" })},),jsx(RadixThemesSelect.Content,{position:"popper"},jsx(Select__group_da859e5be41a722f6cd81ea69baaf2ac,{},)))
  )
}


function Button_b955f5350300bcb199590b8a30a26360 () {
  const reflex___state____state__warframe_reflex___state____calculator_state = useContext(StateContexts.reflex___state____state__warframe_reflex___state____calculator_state)
const [addEvents, connectErrors] = useContext(EventLoopContext);

const on_click_c26477985ead69d65f616979c25b1875 = useCallback(((_e) => (addEvents([(ReflexEvent("reflex___state____state.warframe_reflex___state____calculator_state.add_slot_field", ({ ["index"] : 7 }), ({  })))], [_e], ({  })))), [addEvents, ReflexEvent])

  return (
    jsx(RadixThemesButton,{className:"icon-button field-action-button",disabled:(reflex___state____state__warframe_reflex___state____calculator_state.slot_available_fields_rx_state_?.at?.(7).length?.valueOf?.() === 0?.valueOf?.()),onClick:on_click_c26477985ead69d65f616979c25b1875},"+")
  )
}


function Flex_57d8d95a57f1863209988ff4760944e1 () {
  const reflex___state____state__warframe_reflex___state____calculator_state = useContext(StateContexts.reflex___state____state__warframe_reflex___state____calculator_state)
const [addEvents, connectErrors] = useContext(EventLoopContext);



  return (
    jsx(RadixThemesFlex,{align:"start",className:"rx-Stack",css:({ ["width"] : "100%", ["gap"] : "2" }),direction:"column",gap:"3"},Array.prototype.map.call(reflex___state____state__warframe_reflex___state____calculator_state.slot_fields_rx_state_?.at?.(7) ?? [],((field_rx_state_,index_ad9d7b81e0e65a5948a3885101cbe585)=>(jsx(RadixThemesGrid,{align:"center",columns:"84px minmax(0, 1fr) 32px",css:({ ["columnGap"] : "8px", ["width"] : "100%" }),key:index_ad9d7b81e0e65a5948a3885101cbe585},jsx(RadixThemesText,{as:"p",className:"compact-label"},field_rx_state_?.["label"]),jsx(DebounceInput,{css:({ ["debounceTimeout"] : 250, ["width"] : "100%" }),debounceTimeout:250,element:RadixThemesTextField.Root,max:field_rx_state_?.["max_value"],min:field_rx_state_?.["min_value"],onChange:((_e) => (addEvents([(ReflexEvent("reflex___state____state.warframe_reflex___state____calculator_state.set_slot_field_value", ({ ["index"] : 7, ["field_name"] : field_rx_state_?.["name"], ["value"] : _e?.["target"]?.["value"] }), ({  })))], [_e], ({  })))),step:(field_rx_state_?.["integer"] ? "1" : "0.001"),type:"number",value:(isNotNullOrUndefined(field_rx_state_?.["value"]) ? field_rx_state_?.["value"] : "")},),jsx(RadixThemesButton,{className:"icon-button field-action-button",onClick:((_e) => (addEvents([(ReflexEvent("reflex___state____state.warframe_reflex___state____calculator_state.remove_slot_field", ({ ["index"] : 7, ["field_name"] : field_rx_state_?.["name"] }), ({  })))], [_e], ({  })))),variant:"soft"},"\u00d7"))))))
  )
}


function Fragment_fb562c97925d5220bc779edd06ab2b55 () {
  const reflex___state____state__warframe_reflex___state____calculator_state = useContext(StateContexts.reflex___state____state__warframe_reflex___state____calculator_state)



  return (
    jsx(Fragment,{},((reflex___state____state__warframe_reflex___state____calculator_state.slot_fields_rx_state_?.at?.(7).length > 0)?(jsx(Fragment,{},jsx(Flex_57d8d95a57f1863209988ff4760944e1,{},))):(jsx(Fragment,{},jsx(RadixThemesText,{as:"p",className:"empty-text"},"No custom stats added.")))))
  )
}


function Fragment_e9e9380e1bb00ab0ca7394dc1e0cecd4 () {
  const reflex___state____state__warframe_reflex___state____calculator_state = useContext(StateContexts.reflex___state____state__warframe_reflex___state____calculator_state)



  return (
    jsx(Fragment,{},(!((reflex___state____state__warframe_reflex___state____calculator_state.slot_selected_upgrades_rx_state_?.at?.(7)?.valueOf?.() === "Custom"?.valueOf?.()))?(jsx(Fragment,{},jsx(RadixThemesFlex,{align:"start",className:"rx-Stack",css:({ ["width"] : "100%", ["gap"] : "3" }),direction:"column",gap:"3"},jsx(RadixThemesGrid,{columns:"repeat(2, minmax(0, 1fr))",css:({ ["columnGap"] : "8px", ["width"] : "100%" })},jsx(RadixThemesFlex,{align:"start",className:"rx-Stack",css:({ ["gap"] : "1", ["width"] : "100%" }),direction:"column",gap:"3"},jsx(RadixThemesText,{as:"p",className:"field-label"},"Rank"),jsx(Debounceinput_65044447264598cd6e3d467977a9e84a,{},)),jsx(Fragment_7757b9e9d1bee5d3aa8e128fd17e19a2,{},)),jsx(Fragment_2ac953744385db7adf9339ba188c0049,{},),jsx(RadixThemesSeparator,{css:({ ["width"] : "100%" }),size:"4"},),jsx(Fragment_727d0e4b29d62e947bd26ccac3fcbc69,{},)))):(jsx(Fragment,{},jsx(RadixThemesFlex,{align:"start",className:"rx-Stack",css:({ ["width"] : "100%", ["gap"] : "3" }),direction:"column",gap:"3"},jsx(RadixThemesGrid,{columns:"minmax(0, 1fr) 32px",css:({ ["columnGap"] : "8px", ["width"] : "100%" })},jsx(Select__root_e687dd8ba6a833296c4ba574907b04e5,{},),jsx(Button_b955f5350300bcb199590b8a30a26360,{},)),jsx(Fragment_fb562c97925d5220bc779edd06ab2b55,{},),jsx(RadixThemesSeparator,{css:({ ["width"] : "100%" }),size:"4"},),jsx(Fragment_727d0e4b29d62e947bd26ccac3fcbc69,{},))))))
  )
}


function Badge_15dfe03d30c8421c3728447ff3b853cc () {
  const reflex___state____state__warframe_reflex___state____calculator_state = useContext(StateContexts.reflex___state____state__warframe_reflex___state____calculator_state)



  return (
    jsx(RadixThemesBadge,{className:"contribution-badge",variant:"soft"},reflex___state____state__warframe_reflex___state____calculator_state.slot_contributions_rx_state_?.at?.(8))
  )
}


function Select__root_e5e78961d9e0d27418c5718495b402cb () {
  const reflex___state____state__warframe_reflex___state____calculator_state = useContext(StateContexts.reflex___state____state__warframe_reflex___state____calculator_state)
const [addEvents, connectErrors] = useContext(EventLoopContext);

const on_change_220cb7f4324db2e7c241638904b39b35 = useCallback(((_ev_0) => (addEvents([(ReflexEvent("reflex___state____state.warframe_reflex___state____calculator_state.set_slot_upgrade", ({ ["index"] : 8, ["value"] : _ev_0 }), ({  })))], [_ev_0], ({  })))), [addEvents, ReflexEvent])

  return (
    jsx(RadixThemesSelect.Root,{onValueChange:on_change_220cb7f4324db2e7c241638904b39b35,value:reflex___state____state__warframe_reflex___state____calculator_state.slot_selected_upgrades_rx_state_?.at?.(8)},jsx(RadixThemesSelect.Trigger,{css:({ ["width"] : "100%" })},),jsx(RadixThemesSelect.Content,{position:"popper"},jsx(Select__group_a3ecac2495351b434ca1713de89fa7a8,{},)))
  )
}


function Debounceinput_269fc11f275a49e8db2ff57d587a9015 () {
  const reflex___state____state__warframe_reflex___state____calculator_state = useContext(StateContexts.reflex___state____state__warframe_reflex___state____calculator_state)
const [addEvents, connectErrors] = useContext(EventLoopContext);

const on_change_b3007e058fad1f5080e3f940f0134765 = useCallback(((_e) => (addEvents([(ReflexEvent("reflex___state____state.warframe_reflex___state____calculator_state.set_slot_rank", ({ ["index"] : 8, ["value"] : _e?.["target"]?.["value"] }), ({  })))], [_e], ({  })))), [addEvents, ReflexEvent])

  return (
    jsx(DebounceInput,{css:({ ["width"] : "100%", ["debounceTimeout"] : 250 }),debounceTimeout:250,element:RadixThemesTextField.Root,max:reflex___state____state__warframe_reflex___state____calculator_state.slot_max_ranks_rx_state_?.at?.(8),min:0,onChange:on_change_b3007e058fad1f5080e3f940f0134765,step:"1",type:"number",value:(isNotNullOrUndefined(reflex___state____state__warframe_reflex___state____calculator_state.slot_ranks_rx_state_?.at?.(8)) ? reflex___state____state__warframe_reflex___state____calculator_state.slot_ranks_rx_state_?.at?.(8) : "")},)
  )
}


function Debounceinput_d680d372c2a8129fdc8a348ee40b1da3 () {
  const reflex___state____state__warframe_reflex___state____calculator_state = useContext(StateContexts.reflex___state____state__warframe_reflex___state____calculator_state)
const [addEvents, connectErrors] = useContext(EventLoopContext);

const on_change_20728476ab0ea63e99182921e64f9131 = useCallback(((_e) => (addEvents([(ReflexEvent("reflex___state____state.warframe_reflex___state____calculator_state.set_slot_stacks", ({ ["index"] : 8, ["value"] : _e?.["target"]?.["value"] }), ({  })))], [_e], ({  })))), [addEvents, ReflexEvent])

  return (
    jsx(DebounceInput,{css:({ ["width"] : "100%", ["debounceTimeout"] : 250 }),debounceTimeout:250,element:RadixThemesTextField.Root,max:reflex___state____state__warframe_reflex___state____calculator_state.slot_max_stacks_rx_state_?.at?.(8),min:0,onChange:on_change_20728476ab0ea63e99182921e64f9131,step:"1",type:"number",value:(isNotNullOrUndefined(reflex___state____state__warframe_reflex___state____calculator_state.slot_stacks_rx_state_?.at?.(8)) ? reflex___state____state__warframe_reflex___state____calculator_state.slot_stacks_rx_state_?.at?.(8) : "")},)
  )
}


function Fragment_9780d402b4d37a99c6d9c7ff33d128fd () {
  const reflex___state____state__warframe_reflex___state____calculator_state = useContext(StateContexts.reflex___state____state__warframe_reflex___state____calculator_state)



  return (
    jsx(Fragment,{},((reflex___state____state__warframe_reflex___state____calculator_state.slot_max_stacks_rx_state_?.at?.(8) > 0)?(jsx(Fragment,{},jsx(RadixThemesFlex,{align:"start",className:"rx-Stack",css:({ ["gap"] : "1", ["width"] : "100%" }),direction:"column",gap:"3"},jsx(RadixThemesText,{as:"p",className:"field-label"},"Stacks"),jsx(Debounceinput_d680d372c2a8129fdc8a348ee40b1da3,{},)))):(jsx(Fragment,{},))))
  )
}


function Checkbox_c9776dc7e643cbb7bc14bc15b02b8190 () {
  const reflex___state____state__warframe_reflex___state____calculator_state = useContext(StateContexts.reflex___state____state__warframe_reflex___state____calculator_state)
const [addEvents, connectErrors] = useContext(EventLoopContext);

const on_change_20b4bb5ea5cb6a9c8aff402b285024f5 = useCallback(((_ev_0) => (addEvents([(ReflexEvent("reflex___state____state.warframe_reflex___state____calculator_state.set_slot_condition", ({ ["index"] : 8, ["value"] : _ev_0 }), ({  })))], [_ev_0], ({  })))), [addEvents, ReflexEvent])

  return (
    jsx(RadixThemesCheckbox,{checked:reflex___state____state__warframe_reflex___state____calculator_state.slot_conditions_enabled_rx_state_?.at?.(8),className:"conditional-checkbox-control",onCheckedChange:on_change_20b4bb5ea5cb6a9c8aff402b285024f5,size:"2"},)
  )
}


function Text_dc10e64cf643499530e71d7c01cf87e4 () {
  const reflex___state____state__warframe_reflex___state____calculator_state = useContext(StateContexts.reflex___state____state__warframe_reflex___state____calculator_state)



  return (
    jsx(RadixThemesText,{as:"p",className:"conditional-checkbox-label"},"Enable conditional: ",reflex___state____state__warframe_reflex___state____calculator_state.slot_condition_labels_rx_state_?.at?.(8))
  )
}


function Fragment_e40802252a5a01000d23bccf2a86cd49 () {
  const reflex___state____state__warframe_reflex___state____calculator_state = useContext(StateContexts.reflex___state____state__warframe_reflex___state____calculator_state)



  return (
    jsx(Fragment,{},(reflex___state____state__warframe_reflex___state____calculator_state.slot_has_conditionals_rx_state_?.at?.(8)?(jsx(Fragment,{},jsx(RadixThemesFlex,{align:"start",className:"rx-Stack conditional-checkbox-row",direction:"row",gap:"3"},jsx(RadixThemesText,{as:"label",size:"2"},jsx(RadixThemesFlex,{gap:"2"},jsx(Checkbox_c9776dc7e643cbb7bc14bc15b02b8190,{},),"")),jsx(Text_dc10e64cf643499530e71d7c01cf87e4,{},)))):(jsx(Fragment,{},))))
  )
}


function Flex_fd058dc3bdabb37fc52d4694d2fed510 () {
  const reflex___state____state__warframe_reflex___state____calculator_state = useContext(StateContexts.reflex___state____state__warframe_reflex___state____calculator_state)



  return (
    jsx(RadixThemesFlex,{align:"start",className:"rx-Stack",css:({ ["width"] : "100%", ["gap"] : "1" }),direction:"column",gap:"3"},Array.prototype.map.call(reflex___state____state__warframe_reflex___state____calculator_state.slot_stat_rows_rx_state_?.at?.(8) ?? [],((row_rx_state_,index_6f0cc146e9e04bdc4ed627113713c33a)=>(jsx(RadixThemesFlex,{align:"center",className:"rx-Stack",css:({ ["width"] : "100%" }),direction:"row",key:index_6f0cc146e9e04bdc4ed627113713c33a,gap:"3"},jsx(RadixThemesText,{as:"p",className:"preview-label"},row_rx_state_?.["label"]),jsx(RadixThemesFlex,{css:({ ["flex"] : 1, ["justifySelf"] : "stretch", ["alignSelf"] : "stretch" })},),jsx(RadixThemesText,{as:"p",className:"preview-value"},row_rx_state_?.["value"]))))))
  )
}


function Fragment_49fdd0e299a6c448e95a09e94e70b71a () {
  const reflex___state____state__warframe_reflex___state____calculator_state = useContext(StateContexts.reflex___state____state__warframe_reflex___state____calculator_state)



  return (
    jsx(Fragment,{},((reflex___state____state__warframe_reflex___state____calculator_state.slot_stat_rows_rx_state_?.at?.(8).length > 0)?(jsx(Fragment,{},jsx(Flex_fd058dc3bdabb37fc52d4694d2fed510,{},))):(jsx(Fragment,{},jsx(RadixThemesText,{as:"p",className:"empty-text"},"No stats.")))))
  )
}


function Select__group_c5c9be7018e034725150727c8079935d () {
  const reflex___state____state__warframe_reflex___state____calculator_state = useContext(StateContexts.reflex___state____state__warframe_reflex___state____calculator_state)



  return (
    jsx(RadixThemesSelect.Group,{},"",Array.prototype.map.call(reflex___state____state__warframe_reflex___state____calculator_state.slot_available_fields_rx_state_?.at?.(8) ?? [],((item_rx_state_,index_d6d6157c99650830f12a866606ea87b7)=>(jsx(RadixThemesSelect.Item,{key:index_d6d6157c99650830f12a866606ea87b7,value:item_rx_state_},item_rx_state_)))))
  )
}


function Select__root_574c26b78a7cc2b63b458284a79c38b1 () {
  const reflex___state____state__warframe_reflex___state____calculator_state = useContext(StateContexts.reflex___state____state__warframe_reflex___state____calculator_state)
const [addEvents, connectErrors] = useContext(EventLoopContext);

const on_change_6412d32e2c083642625fca2063f286ef = useCallback(((_ev_0) => (addEvents([(ReflexEvent("reflex___state____state.warframe_reflex___state____calculator_state.set_slot_pending_field", ({ ["index"] : 8, ["value"] : _ev_0 }), ({  })))], [_ev_0], ({  })))), [addEvents, ReflexEvent])

  return (
    jsx(RadixThemesSelect.Root,{disabled:(reflex___state____state__warframe_reflex___state____calculator_state.slot_available_fields_rx_state_?.at?.(8).length?.valueOf?.() === 0?.valueOf?.()),onValueChange:on_change_6412d32e2c083642625fca2063f286ef,value:reflex___state____state__warframe_reflex___state____calculator_state.slot_pending_fields_rx_state_?.at?.(8)},jsx(RadixThemesSelect.Trigger,{css:({ ["width"] : "100%" })},),jsx(RadixThemesSelect.Content,{position:"popper"},jsx(Select__group_c5c9be7018e034725150727c8079935d,{},)))
  )
}


function Button_f772e795cc6c3e9ddfce2f44acfd66c5 () {
  const reflex___state____state__warframe_reflex___state____calculator_state = useContext(StateContexts.reflex___state____state__warframe_reflex___state____calculator_state)
const [addEvents, connectErrors] = useContext(EventLoopContext);

const on_click_f9120bdd5e8caeadb64026b1d996b590 = useCallback(((_e) => (addEvents([(ReflexEvent("reflex___state____state.warframe_reflex___state____calculator_state.add_slot_field", ({ ["index"] : 8 }), ({  })))], [_e], ({  })))), [addEvents, ReflexEvent])

  return (
    jsx(RadixThemesButton,{className:"icon-button field-action-button",disabled:(reflex___state____state__warframe_reflex___state____calculator_state.slot_available_fields_rx_state_?.at?.(8).length?.valueOf?.() === 0?.valueOf?.()),onClick:on_click_f9120bdd5e8caeadb64026b1d996b590},"+")
  )
}


function Flex_472f4ebcccc4c00266a3042d1d9c487b () {
  const reflex___state____state__warframe_reflex___state____calculator_state = useContext(StateContexts.reflex___state____state__warframe_reflex___state____calculator_state)
const [addEvents, connectErrors] = useContext(EventLoopContext);



  return (
    jsx(RadixThemesFlex,{align:"start",className:"rx-Stack",css:({ ["width"] : "100%", ["gap"] : "2" }),direction:"column",gap:"3"},Array.prototype.map.call(reflex___state____state__warframe_reflex___state____calculator_state.slot_fields_rx_state_?.at?.(8) ?? [],((field_rx_state_,index_ad9d7b81e0e65a5948a3885101cbe585)=>(jsx(RadixThemesGrid,{align:"center",columns:"84px minmax(0, 1fr) 32px",css:({ ["columnGap"] : "8px", ["width"] : "100%" }),key:index_ad9d7b81e0e65a5948a3885101cbe585},jsx(RadixThemesText,{as:"p",className:"compact-label"},field_rx_state_?.["label"]),jsx(DebounceInput,{css:({ ["debounceTimeout"] : 250, ["width"] : "100%" }),debounceTimeout:250,element:RadixThemesTextField.Root,max:field_rx_state_?.["max_value"],min:field_rx_state_?.["min_value"],onChange:((_e) => (addEvents([(ReflexEvent("reflex___state____state.warframe_reflex___state____calculator_state.set_slot_field_value", ({ ["index"] : 8, ["field_name"] : field_rx_state_?.["name"], ["value"] : _e?.["target"]?.["value"] }), ({  })))], [_e], ({  })))),step:(field_rx_state_?.["integer"] ? "1" : "0.001"),type:"number",value:(isNotNullOrUndefined(field_rx_state_?.["value"]) ? field_rx_state_?.["value"] : "")},),jsx(RadixThemesButton,{className:"icon-button field-action-button",onClick:((_e) => (addEvents([(ReflexEvent("reflex___state____state.warframe_reflex___state____calculator_state.remove_slot_field", ({ ["index"] : 8, ["field_name"] : field_rx_state_?.["name"] }), ({  })))], [_e], ({  })))),variant:"soft"},"\u00d7"))))))
  )
}


function Fragment_4922f0acf6f6007173554d1ff4ecb0d8 () {
  const reflex___state____state__warframe_reflex___state____calculator_state = useContext(StateContexts.reflex___state____state__warframe_reflex___state____calculator_state)



  return (
    jsx(Fragment,{},((reflex___state____state__warframe_reflex___state____calculator_state.slot_fields_rx_state_?.at?.(8).length > 0)?(jsx(Fragment,{},jsx(Flex_472f4ebcccc4c00266a3042d1d9c487b,{},))):(jsx(Fragment,{},jsx(RadixThemesText,{as:"p",className:"empty-text"},"No custom stats added.")))))
  )
}


function Fragment_31a778764de21a99e847ebdc51f08e07 () {
  const reflex___state____state__warframe_reflex___state____calculator_state = useContext(StateContexts.reflex___state____state__warframe_reflex___state____calculator_state)



  return (
    jsx(Fragment,{},(!((reflex___state____state__warframe_reflex___state____calculator_state.slot_selected_upgrades_rx_state_?.at?.(8)?.valueOf?.() === "Custom"?.valueOf?.()))?(jsx(Fragment,{},jsx(RadixThemesFlex,{align:"start",className:"rx-Stack",css:({ ["width"] : "100%", ["gap"] : "3" }),direction:"column",gap:"3"},jsx(RadixThemesGrid,{columns:"repeat(2, minmax(0, 1fr))",css:({ ["columnGap"] : "8px", ["width"] : "100%" })},jsx(RadixThemesFlex,{align:"start",className:"rx-Stack",css:({ ["gap"] : "1", ["width"] : "100%" }),direction:"column",gap:"3"},jsx(RadixThemesText,{as:"p",className:"field-label"},"Rank"),jsx(Debounceinput_269fc11f275a49e8db2ff57d587a9015,{},)),jsx(Fragment_9780d402b4d37a99c6d9c7ff33d128fd,{},)),jsx(Fragment_e40802252a5a01000d23bccf2a86cd49,{},),jsx(RadixThemesSeparator,{css:({ ["width"] : "100%" }),size:"4"},),jsx(Fragment_49fdd0e299a6c448e95a09e94e70b71a,{},)))):(jsx(Fragment,{},jsx(RadixThemesFlex,{align:"start",className:"rx-Stack",css:({ ["width"] : "100%", ["gap"] : "3" }),direction:"column",gap:"3"},jsx(RadixThemesGrid,{columns:"minmax(0, 1fr) 32px",css:({ ["columnGap"] : "8px", ["width"] : "100%" })},jsx(Select__root_574c26b78a7cc2b63b458284a79c38b1,{},),jsx(Button_f772e795cc6c3e9ddfce2f44acfd66c5,{},)),jsx(Fragment_4922f0acf6f6007173554d1ff4ecb0d8,{},),jsx(RadixThemesSeparator,{css:({ ["width"] : "100%" }),size:"4"},),jsx(Fragment_49fdd0e299a6c448e95a09e94e70b71a,{},))))))
  )
}


function Badge_6dea4a56dc58fbf481d7731c19dbd331 () {
  const reflex___state____state__warframe_reflex___state____calculator_state = useContext(StateContexts.reflex___state____state__warframe_reflex___state____calculator_state)



  return (
    jsx(RadixThemesBadge,{className:"contribution-badge",variant:"soft"},reflex___state____state__warframe_reflex___state____calculator_state.slot_contributions_rx_state_?.at?.(9))
  )
}


function Select__group_4f9131f5b8b93941c07f0d370f1c922b () {
  const reflex___state____state__warframe_reflex___state____calculator_state = useContext(StateContexts.reflex___state____state__warframe_reflex___state____calculator_state)



  return (
    jsx(RadixThemesSelect.Group,{},"",Array.prototype.map.call(reflex___state____state__warframe_reflex___state____calculator_state.exilus_options_rx_state_ ?? [],((item_rx_state_,index_d6d6157c99650830f12a866606ea87b7)=>(jsx(RadixThemesSelect.Item,{key:index_d6d6157c99650830f12a866606ea87b7,value:item_rx_state_},item_rx_state_)))))
  )
}


function Select__root_e99e6b3d9948c86064153089032ef7b7 () {
  const reflex___state____state__warframe_reflex___state____calculator_state = useContext(StateContexts.reflex___state____state__warframe_reflex___state____calculator_state)
const [addEvents, connectErrors] = useContext(EventLoopContext);

const on_change_21d01d61d2c5e5c67d4f39150e86a93a = useCallback(((_ev_0) => (addEvents([(ReflexEvent("reflex___state____state.warframe_reflex___state____calculator_state.set_slot_upgrade", ({ ["index"] : 9, ["value"] : _ev_0 }), ({  })))], [_ev_0], ({  })))), [addEvents, ReflexEvent])

  return (
    jsx(RadixThemesSelect.Root,{onValueChange:on_change_21d01d61d2c5e5c67d4f39150e86a93a,value:reflex___state____state__warframe_reflex___state____calculator_state.slot_selected_upgrades_rx_state_?.at?.(9)},jsx(RadixThemesSelect.Trigger,{css:({ ["width"] : "100%" })},),jsx(RadixThemesSelect.Content,{position:"popper"},jsx(Select__group_4f9131f5b8b93941c07f0d370f1c922b,{},)))
  )
}


function Debounceinput_13b2c95d4189648abe30f5de85df200f () {
  const reflex___state____state__warframe_reflex___state____calculator_state = useContext(StateContexts.reflex___state____state__warframe_reflex___state____calculator_state)
const [addEvents, connectErrors] = useContext(EventLoopContext);

const on_change_0e58c9e158ff02542f84abb0af5f60c8 = useCallback(((_e) => (addEvents([(ReflexEvent("reflex___state____state.warframe_reflex___state____calculator_state.set_slot_rank", ({ ["index"] : 9, ["value"] : _e?.["target"]?.["value"] }), ({  })))], [_e], ({  })))), [addEvents, ReflexEvent])

  return (
    jsx(DebounceInput,{css:({ ["width"] : "100%", ["debounceTimeout"] : 250 }),debounceTimeout:250,element:RadixThemesTextField.Root,max:reflex___state____state__warframe_reflex___state____calculator_state.slot_max_ranks_rx_state_?.at?.(9),min:0,onChange:on_change_0e58c9e158ff02542f84abb0af5f60c8,step:"1",type:"number",value:(isNotNullOrUndefined(reflex___state____state__warframe_reflex___state____calculator_state.slot_ranks_rx_state_?.at?.(9)) ? reflex___state____state__warframe_reflex___state____calculator_state.slot_ranks_rx_state_?.at?.(9) : "")},)
  )
}


function Debounceinput_e14816c744adf9323d6f110d46e37d71 () {
  const reflex___state____state__warframe_reflex___state____calculator_state = useContext(StateContexts.reflex___state____state__warframe_reflex___state____calculator_state)
const [addEvents, connectErrors] = useContext(EventLoopContext);

const on_change_3d2fee9f681fab338664265db404a077 = useCallback(((_e) => (addEvents([(ReflexEvent("reflex___state____state.warframe_reflex___state____calculator_state.set_slot_stacks", ({ ["index"] : 9, ["value"] : _e?.["target"]?.["value"] }), ({  })))], [_e], ({  })))), [addEvents, ReflexEvent])

  return (
    jsx(DebounceInput,{css:({ ["width"] : "100%", ["debounceTimeout"] : 250 }),debounceTimeout:250,element:RadixThemesTextField.Root,max:reflex___state____state__warframe_reflex___state____calculator_state.slot_max_stacks_rx_state_?.at?.(9),min:0,onChange:on_change_3d2fee9f681fab338664265db404a077,step:"1",type:"number",value:(isNotNullOrUndefined(reflex___state____state__warframe_reflex___state____calculator_state.slot_stacks_rx_state_?.at?.(9)) ? reflex___state____state__warframe_reflex___state____calculator_state.slot_stacks_rx_state_?.at?.(9) : "")},)
  )
}


function Fragment_fa81364c8f8a1ba92ed7c53454181cae () {
  const reflex___state____state__warframe_reflex___state____calculator_state = useContext(StateContexts.reflex___state____state__warframe_reflex___state____calculator_state)



  return (
    jsx(Fragment,{},((reflex___state____state__warframe_reflex___state____calculator_state.slot_max_stacks_rx_state_?.at?.(9) > 0)?(jsx(Fragment,{},jsx(RadixThemesFlex,{align:"start",className:"rx-Stack",css:({ ["gap"] : "1", ["width"] : "100%" }),direction:"column",gap:"3"},jsx(RadixThemesText,{as:"p",className:"field-label"},"Stacks"),jsx(Debounceinput_e14816c744adf9323d6f110d46e37d71,{},)))):(jsx(Fragment,{},))))
  )
}


function Checkbox_49392c1c2dc2171b61d9b79cc8b6b15c () {
  const reflex___state____state__warframe_reflex___state____calculator_state = useContext(StateContexts.reflex___state____state__warframe_reflex___state____calculator_state)
const [addEvents, connectErrors] = useContext(EventLoopContext);

const on_change_82926cb77cca786000893c9792ebec59 = useCallback(((_ev_0) => (addEvents([(ReflexEvent("reflex___state____state.warframe_reflex___state____calculator_state.set_slot_condition", ({ ["index"] : 9, ["value"] : _ev_0 }), ({  })))], [_ev_0], ({  })))), [addEvents, ReflexEvent])

  return (
    jsx(RadixThemesCheckbox,{checked:reflex___state____state__warframe_reflex___state____calculator_state.slot_conditions_enabled_rx_state_?.at?.(9),className:"conditional-checkbox-control",onCheckedChange:on_change_82926cb77cca786000893c9792ebec59,size:"2"},)
  )
}


function Text_df803d9a9d2eb255ca7050d84ee58650 () {
  const reflex___state____state__warframe_reflex___state____calculator_state = useContext(StateContexts.reflex___state____state__warframe_reflex___state____calculator_state)



  return (
    jsx(RadixThemesText,{as:"p",className:"conditional-checkbox-label"},"Enable conditional: ",reflex___state____state__warframe_reflex___state____calculator_state.slot_condition_labels_rx_state_?.at?.(9))
  )
}


function Fragment_33d086d5d1b0a226a13f86423dcbf6d3 () {
  const reflex___state____state__warframe_reflex___state____calculator_state = useContext(StateContexts.reflex___state____state__warframe_reflex___state____calculator_state)



  return (
    jsx(Fragment,{},(reflex___state____state__warframe_reflex___state____calculator_state.slot_has_conditionals_rx_state_?.at?.(9)?(jsx(Fragment,{},jsx(RadixThemesFlex,{align:"start",className:"rx-Stack conditional-checkbox-row",direction:"row",gap:"3"},jsx(RadixThemesText,{as:"label",size:"2"},jsx(RadixThemesFlex,{gap:"2"},jsx(Checkbox_49392c1c2dc2171b61d9b79cc8b6b15c,{},),"")),jsx(Text_df803d9a9d2eb255ca7050d84ee58650,{},)))):(jsx(Fragment,{},))))
  )
}


function Flex_860a108dbc1356e3d07dc0d78b893509 () {
  const reflex___state____state__warframe_reflex___state____calculator_state = useContext(StateContexts.reflex___state____state__warframe_reflex___state____calculator_state)



  return (
    jsx(RadixThemesFlex,{align:"start",className:"rx-Stack",css:({ ["width"] : "100%", ["gap"] : "1" }),direction:"column",gap:"3"},Array.prototype.map.call(reflex___state____state__warframe_reflex___state____calculator_state.slot_stat_rows_rx_state_?.at?.(9) ?? [],((row_rx_state_,index_6f0cc146e9e04bdc4ed627113713c33a)=>(jsx(RadixThemesFlex,{align:"center",className:"rx-Stack",css:({ ["width"] : "100%" }),direction:"row",key:index_6f0cc146e9e04bdc4ed627113713c33a,gap:"3"},jsx(RadixThemesText,{as:"p",className:"preview-label"},row_rx_state_?.["label"]),jsx(RadixThemesFlex,{css:({ ["flex"] : 1, ["justifySelf"] : "stretch", ["alignSelf"] : "stretch" })},),jsx(RadixThemesText,{as:"p",className:"preview-value"},row_rx_state_?.["value"]))))))
  )
}


function Fragment_8cce2d9383e8f85e4d557223af295379 () {
  const reflex___state____state__warframe_reflex___state____calculator_state = useContext(StateContexts.reflex___state____state__warframe_reflex___state____calculator_state)



  return (
    jsx(Fragment,{},((reflex___state____state__warframe_reflex___state____calculator_state.slot_stat_rows_rx_state_?.at?.(9).length > 0)?(jsx(Fragment,{},jsx(Flex_860a108dbc1356e3d07dc0d78b893509,{},))):(jsx(Fragment,{},jsx(RadixThemesText,{as:"p",className:"empty-text"},"No stats.")))))
  )
}


function Select__group_f22d88b2498900067704c8ea9f58d557 () {
  const reflex___state____state__warframe_reflex___state____calculator_state = useContext(StateContexts.reflex___state____state__warframe_reflex___state____calculator_state)



  return (
    jsx(RadixThemesSelect.Group,{},"",Array.prototype.map.call(reflex___state____state__warframe_reflex___state____calculator_state.slot_available_fields_rx_state_?.at?.(9) ?? [],((item_rx_state_,index_d6d6157c99650830f12a866606ea87b7)=>(jsx(RadixThemesSelect.Item,{key:index_d6d6157c99650830f12a866606ea87b7,value:item_rx_state_},item_rx_state_)))))
  )
}


function Select__root_748e5835ad6a741ba215b90de9ab7d70 () {
  const reflex___state____state__warframe_reflex___state____calculator_state = useContext(StateContexts.reflex___state____state__warframe_reflex___state____calculator_state)
const [addEvents, connectErrors] = useContext(EventLoopContext);

const on_change_39418f3de817a4c3642ca026ee77b6cf = useCallback(((_ev_0) => (addEvents([(ReflexEvent("reflex___state____state.warframe_reflex___state____calculator_state.set_slot_pending_field", ({ ["index"] : 9, ["value"] : _ev_0 }), ({  })))], [_ev_0], ({  })))), [addEvents, ReflexEvent])

  return (
    jsx(RadixThemesSelect.Root,{disabled:(reflex___state____state__warframe_reflex___state____calculator_state.slot_available_fields_rx_state_?.at?.(9).length?.valueOf?.() === 0?.valueOf?.()),onValueChange:on_change_39418f3de817a4c3642ca026ee77b6cf,value:reflex___state____state__warframe_reflex___state____calculator_state.slot_pending_fields_rx_state_?.at?.(9)},jsx(RadixThemesSelect.Trigger,{css:({ ["width"] : "100%" })},),jsx(RadixThemesSelect.Content,{position:"popper"},jsx(Select__group_f22d88b2498900067704c8ea9f58d557,{},)))
  )
}


function Button_474f111b3228f8aa1bd8d973c6557ad3 () {
  const reflex___state____state__warframe_reflex___state____calculator_state = useContext(StateContexts.reflex___state____state__warframe_reflex___state____calculator_state)
const [addEvents, connectErrors] = useContext(EventLoopContext);

const on_click_7c3720491bae1503b3785cc51111d462 = useCallback(((_e) => (addEvents([(ReflexEvent("reflex___state____state.warframe_reflex___state____calculator_state.add_slot_field", ({ ["index"] : 9 }), ({  })))], [_e], ({  })))), [addEvents, ReflexEvent])

  return (
    jsx(RadixThemesButton,{className:"icon-button field-action-button",disabled:(reflex___state____state__warframe_reflex___state____calculator_state.slot_available_fields_rx_state_?.at?.(9).length?.valueOf?.() === 0?.valueOf?.()),onClick:on_click_7c3720491bae1503b3785cc51111d462},"+")
  )
}


function Flex_f7118a0689bcd561d568107946b07eae () {
  const reflex___state____state__warframe_reflex___state____calculator_state = useContext(StateContexts.reflex___state____state__warframe_reflex___state____calculator_state)
const [addEvents, connectErrors] = useContext(EventLoopContext);



  return (
    jsx(RadixThemesFlex,{align:"start",className:"rx-Stack",css:({ ["width"] : "100%", ["gap"] : "2" }),direction:"column",gap:"3"},Array.prototype.map.call(reflex___state____state__warframe_reflex___state____calculator_state.slot_fields_rx_state_?.at?.(9) ?? [],((field_rx_state_,index_ad9d7b81e0e65a5948a3885101cbe585)=>(jsx(RadixThemesGrid,{align:"center",columns:"84px minmax(0, 1fr) 32px",css:({ ["columnGap"] : "8px", ["width"] : "100%" }),key:index_ad9d7b81e0e65a5948a3885101cbe585},jsx(RadixThemesText,{as:"p",className:"compact-label"},field_rx_state_?.["label"]),jsx(DebounceInput,{css:({ ["debounceTimeout"] : 250, ["width"] : "100%" }),debounceTimeout:250,element:RadixThemesTextField.Root,max:field_rx_state_?.["max_value"],min:field_rx_state_?.["min_value"],onChange:((_e) => (addEvents([(ReflexEvent("reflex___state____state.warframe_reflex___state____calculator_state.set_slot_field_value", ({ ["index"] : 9, ["field_name"] : field_rx_state_?.["name"], ["value"] : _e?.["target"]?.["value"] }), ({  })))], [_e], ({  })))),step:(field_rx_state_?.["integer"] ? "1" : "0.001"),type:"number",value:(isNotNullOrUndefined(field_rx_state_?.["value"]) ? field_rx_state_?.["value"] : "")},),jsx(RadixThemesButton,{className:"icon-button field-action-button",onClick:((_e) => (addEvents([(ReflexEvent("reflex___state____state.warframe_reflex___state____calculator_state.remove_slot_field", ({ ["index"] : 9, ["field_name"] : field_rx_state_?.["name"] }), ({  })))], [_e], ({  })))),variant:"soft"},"\u00d7"))))))
  )
}


function Fragment_fefec4af55d852fcc03f3c29aac5b39b () {
  const reflex___state____state__warframe_reflex___state____calculator_state = useContext(StateContexts.reflex___state____state__warframe_reflex___state____calculator_state)



  return (
    jsx(Fragment,{},((reflex___state____state__warframe_reflex___state____calculator_state.slot_fields_rx_state_?.at?.(9).length > 0)?(jsx(Fragment,{},jsx(Flex_f7118a0689bcd561d568107946b07eae,{},))):(jsx(Fragment,{},jsx(RadixThemesText,{as:"p",className:"empty-text"},"No custom stats added.")))))
  )
}


function Fragment_ce28823ad6aed14e3ae137c9e968e3f9 () {
  const reflex___state____state__warframe_reflex___state____calculator_state = useContext(StateContexts.reflex___state____state__warframe_reflex___state____calculator_state)



  return (
    jsx(Fragment,{},(!((reflex___state____state__warframe_reflex___state____calculator_state.slot_selected_upgrades_rx_state_?.at?.(9)?.valueOf?.() === "Custom"?.valueOf?.()))?(jsx(Fragment,{},jsx(RadixThemesFlex,{align:"start",className:"rx-Stack",css:({ ["width"] : "100%", ["gap"] : "3" }),direction:"column",gap:"3"},jsx(RadixThemesGrid,{columns:"repeat(2, minmax(0, 1fr))",css:({ ["columnGap"] : "8px", ["width"] : "100%" })},jsx(RadixThemesFlex,{align:"start",className:"rx-Stack",css:({ ["gap"] : "1", ["width"] : "100%" }),direction:"column",gap:"3"},jsx(RadixThemesText,{as:"p",className:"field-label"},"Rank"),jsx(Debounceinput_13b2c95d4189648abe30f5de85df200f,{},)),jsx(Fragment_fa81364c8f8a1ba92ed7c53454181cae,{},)),jsx(Fragment_33d086d5d1b0a226a13f86423dcbf6d3,{},),jsx(RadixThemesSeparator,{css:({ ["width"] : "100%" }),size:"4"},),jsx(Fragment_8cce2d9383e8f85e4d557223af295379,{},)))):(jsx(Fragment,{},jsx(RadixThemesFlex,{align:"start",className:"rx-Stack",css:({ ["width"] : "100%", ["gap"] : "3" }),direction:"column",gap:"3"},jsx(RadixThemesGrid,{columns:"minmax(0, 1fr) 32px",css:({ ["columnGap"] : "8px", ["width"] : "100%" })},jsx(Select__root_748e5835ad6a741ba215b90de9ab7d70,{},),jsx(Button_474f111b3228f8aa1bd8d973c6557ad3,{},)),jsx(Fragment_fefec4af55d852fcc03f3c29aac5b39b,{},),jsx(RadixThemesSeparator,{css:({ ["width"] : "100%" }),size:"4"},),jsx(Fragment_8cce2d9383e8f85e4d557223af295379,{},))))))
  )
}


function Select__group_4afe1098fa916766a34495ef3841b9fb () {
  const reflex___state____state__warframe_reflex___state____calculator_state = useContext(StateContexts.reflex___state____state__warframe_reflex___state____calculator_state)



  return (
    jsx(RadixThemesSelect.Group,{},"",Array.prototype.map.call(reflex___state____state__warframe_reflex___state____calculator_state.external_available_fields_rx_state_ ?? [],((item_rx_state_,index_d6d6157c99650830f12a866606ea87b7)=>(jsx(RadixThemesSelect.Item,{key:index_d6d6157c99650830f12a866606ea87b7,value:item_rx_state_},item_rx_state_)))))
  )
}


function Select__root_8d758698bfde90af9cc3b07a7902b9a5 () {
  const reflex___state____state__warframe_reflex___state____calculator_state = useContext(StateContexts.reflex___state____state__warframe_reflex___state____calculator_state)
const [addEvents, connectErrors] = useContext(EventLoopContext);

const on_change_ff39d8f304ba9879042b873d0705ce10 = useCallback(((_ev_0) => (addEvents([(ReflexEvent("reflex___state____state.warframe_reflex___state____calculator_state.set_external_pending_field", ({ ["value"] : _ev_0 }), ({  })))], [_ev_0], ({  })))), [addEvents, ReflexEvent])

  return (
    jsx(RadixThemesSelect.Root,{disabled:(reflex___state____state__warframe_reflex___state____calculator_state.external_available_fields_rx_state_.length?.valueOf?.() === 0?.valueOf?.()),onValueChange:on_change_ff39d8f304ba9879042b873d0705ce10,value:reflex___state____state__warframe_reflex___state____calculator_state.external_pending_field_rx_state_},jsx(RadixThemesSelect.Trigger,{css:({ ["width"] : "100%" })},),jsx(RadixThemesSelect.Content,{position:"popper"},jsx(Select__group_4afe1098fa916766a34495ef3841b9fb,{},)))
  )
}


function Button_ccd775f90ae81b7a376e2a14287d63a4 () {
  const reflex___state____state__warframe_reflex___state____calculator_state = useContext(StateContexts.reflex___state____state__warframe_reflex___state____calculator_state)
const [addEvents, connectErrors] = useContext(EventLoopContext);

const on_click_24db03c4c9b614f4f3a268e0c10fd66d = useCallback(((_e) => (addEvents([(ReflexEvent("reflex___state____state.warframe_reflex___state____calculator_state.add_external_field", ({  }), ({  })))], [_e], ({  })))), [addEvents, ReflexEvent])

  return (
    jsx(RadixThemesButton,{className:"icon-button",disabled:(reflex___state____state__warframe_reflex___state____calculator_state.external_available_fields_rx_state_.length?.valueOf?.() === 0?.valueOf?.()),onClick:on_click_24db03c4c9b614f4f3a268e0c10fd66d},"+")
  )
}


function Flex_802a4a3fdaa89b5f4177cb8febc516de () {
  const reflex___state____state__warframe_reflex___state____calculator_state = useContext(StateContexts.reflex___state____state__warframe_reflex___state____calculator_state)
const [addEvents, connectErrors] = useContext(EventLoopContext);



  return (
    jsx(RadixThemesFlex,{align:"start",className:"rx-Stack",css:({ ["width"] : "100%", ["gap"] : "2" }),direction:"column",gap:"3"},Array.prototype.map.call(reflex___state____state__warframe_reflex___state____calculator_state.external_fields_rx_state_ ?? [],((field_rx_state_,index_9ccd69f1152ab4ac827d3316d7f75288)=>(jsx(RadixThemesGrid,{align:"center",columns:"110px minmax(0, 1fr) 32px",css:({ ["columnGap"] : "8px", ["width"] : "100%" }),key:index_9ccd69f1152ab4ac827d3316d7f75288},jsx(RadixThemesText,{as:"p",className:"compact-label"},field_rx_state_?.["label"]),jsx(DebounceInput,{css:({ ["debounceTimeout"] : 250, ["width"] : "100%" }),debounceTimeout:250,element:RadixThemesTextField.Root,max:field_rx_state_?.["max_value"],min:field_rx_state_?.["min_value"],onChange:((_e) => (addEvents([(ReflexEvent("reflex___state____state.warframe_reflex___state____calculator_state.set_external_field_value", ({ ["field_name"] : field_rx_state_?.["name"], ["value"] : _e?.["target"]?.["value"] }), ({  })))], [_e], ({  })))),step:(field_rx_state_?.["integer"] ? "1" : "0.001"),type:"number",value:(isNotNullOrUndefined(field_rx_state_?.["value"]) ? field_rx_state_?.["value"] : "")},),jsx(RadixThemesButton,{className:"icon-button",onClick:((_e) => (addEvents([(ReflexEvent("reflex___state____state.warframe_reflex___state____calculator_state.remove_external_field", ({ ["field_name"] : field_rx_state_?.["name"] }), ({  })))], [_e], ({  })))),variant:"soft"},"\u00d7"))))))
  )
}


function Fragment_4642706f68dc54964a6c439554e4dbc9 () {
  const reflex___state____state__warframe_reflex___state____calculator_state = useContext(StateContexts.reflex___state____state__warframe_reflex___state____calculator_state)



  return (
    jsx(Fragment,{},((reflex___state____state__warframe_reflex___state____calculator_state.external_fields_rx_state_.length > 0)?(jsx(Fragment,{},jsx(Flex_802a4a3fdaa89b5f4177cb8febc516de,{},))):(jsx(Fragment,{},jsx(RadixThemesText,{as:"p",className:"empty-text"},"No external buffs added.")))))
  )
}


function Code_1b712006251199d76d293212f1b5c256 () {
  const reflex___state____state__warframe_reflex___state____calculator_state = useContext(StateContexts.reflex___state____state__warframe_reflex___state____calculator_state)



  return (
    jsx(RadixThemesCode,{},reflex___state____state__warframe_reflex___state____calculator_state.result_error_rx_state_)
  )
}


function Fragment_ae1710cba5a9b70e84f39fb8665c58ec () {
  const reflex___state____state__warframe_reflex___state____calculator_state = useContext(StateContexts.reflex___state____state__warframe_reflex___state____calculator_state)



  return (
    jsx(Fragment,{},(reflex___state____state__warframe_reflex___state____calculator_state.has_error_rx_state_?(jsx(Fragment,{},jsx(RadixThemesBox,{className:"error-box",css:({ ["width"] : "100%" })},jsx(RadixThemesText,{as:"p"},"The calculator could not evaluate the current configuration."),jsx(Code_1b712006251199d76d293212f1b5c256,{},)))):(jsx(Fragment,{},))))
  )
}


function Box_9892bbed9e17d8e198cb78fdae1ff274 () {
  const reflex___state____state__warframe_reflex___state____calculator_state = useContext(StateContexts.reflex___state____state__warframe_reflex___state____calculator_state)



  return (
    jsx(RadixThemesBox,{className:"metric-grid",css:({ ["width"] : "100%" })},Array.prototype.map.call(reflex___state____state__warframe_reflex___state____calculator_state.main_result_metrics_rx_state_ ?? [],((metric_rx_state_,index_f87c5bfa448e5bfa1a0ad8ba91a867b3)=>(jsx(RadixThemesBox,{className:"metric-card",key:index_f87c5bfa448e5bfa1a0ad8ba91a867b3},jsx(RadixThemesFlex,{align:"start",className:"rx-Stack",css:({ ["gap"] : "1" }),direction:"column",gap:"3"},jsx(RadixThemesText,{as:"p",className:"metric-label"},metric_rx_state_?.["label"]),jsx(RadixThemesText,{as:"p",className:"metric-value"},metric_rx_state_?.["value"])))))),Array.prototype.map.call(reflex___state____state__warframe_reflex___state____calculator_state.weakpoint_result_metrics_rx_state_ ?? [],((metric_rx_state_,index_f87c5bfa448e5bfa1a0ad8ba91a867b3)=>(jsx(RadixThemesBox,{className:"metric-card",key:index_f87c5bfa448e5bfa1a0ad8ba91a867b3},jsx(RadixThemesFlex,{align:"start",className:"rx-Stack",css:({ ["gap"] : "1" }),direction:"column",gap:"3"},jsx(RadixThemesText,{as:"p",className:"metric-label"},metric_rx_state_?.["label"]),jsx(RadixThemesText,{as:"p",className:"metric-value"},metric_rx_state_?.["value"])))))),Array.prototype.map.call(reflex___state____state__warframe_reflex___state____calculator_state.misc_result_metrics_rx_state_ ?? [],((metric_rx_state_,index_f87c5bfa448e5bfa1a0ad8ba91a867b3)=>(jsx(RadixThemesBox,{className:"metric-card",key:index_f87c5bfa448e5bfa1a0ad8ba91a867b3},jsx(RadixThemesFlex,{align:"start",className:"rx-Stack",css:({ ["gap"] : "1" }),direction:"column",gap:"3"},jsx(RadixThemesText,{as:"p",className:"metric-label"},metric_rx_state_?.["label"]),jsx(RadixThemesText,{as:"p",className:"metric-value"},metric_rx_state_?.["value"])))))))
  )
}


function Box_314a6729391d383876ec34128af42aec () {
  const reflex___state____state__warframe_reflex___state____calculator_state = useContext(StateContexts.reflex___state____state__warframe_reflex___state____calculator_state)



  return (
    jsx(RadixThemesBox,{className:"metric-grid",css:({ ["width"] : "100%" })},Array.prototype.map.call(reflex___state____state__warframe_reflex___state____calculator_state.main_result_metrics_rx_state_ ?? [],((metric_rx_state_,index_f87c5bfa448e5bfa1a0ad8ba91a867b3)=>(jsx(RadixThemesBox,{className:"metric-card",key:index_f87c5bfa448e5bfa1a0ad8ba91a867b3},jsx(RadixThemesFlex,{align:"start",className:"rx-Stack",css:({ ["gap"] : "1" }),direction:"column",gap:"3"},jsx(RadixThemesText,{as:"p",className:"metric-label"},metric_rx_state_?.["label"]),jsx(RadixThemesText,{as:"p",className:"metric-value"},metric_rx_state_?.["value"])))))))
  )
}


function Fragment_aea0fecb057b689ff889ff463e5cd0e0 () {
  const reflex___state____state__warframe_reflex___state____calculator_state = useContext(StateContexts.reflex___state____state__warframe_reflex___state____calculator_state)



  return (
    jsx(Fragment,{},(reflex___state____state__warframe_reflex___state____calculator_state.ranged_weapon_rx_state_?(jsx(Fragment,{},jsx(Box_9892bbed9e17d8e198cb78fdae1ff274,{},))):(jsx(Fragment,{},jsx(Box_314a6729391d383876ec34128af42aec,{},)))))
  )
}


function Table__body_e8f64911eaa72ab5b8579a7197e8a35c () {
  const reflex___state____state__warframe_reflex___state____calculator_state = useContext(StateContexts.reflex___state____state__warframe_reflex___state____calculator_state)



  return (
    jsx(RadixThemesTable.Body,{},Array.prototype.map.call(reflex___state____state__warframe_reflex___state____calculator_state.damage_result_rows_rx_state_ ?? [],((row_rx_state_,index_b010da083c8c1653517f7752910b37d3)=>(jsx(RadixThemesTable.Row,{key:index_b010da083c8c1653517f7752910b37d3},jsx(RadixThemesTable.RowHeaderCell,{},row_rx_state_?.["damage_type"]),jsx(RadixThemesTable.Cell,{},row_rx_state_?.["damage"]),jsx(RadixThemesTable.Cell,{},row_rx_state_?.["weight"]),jsx(RadixThemesTable.Cell,{},row_rx_state_?.["proc_chance"]))))))
  )
}


function Table__body_8721add4af4bc1e4854717eadb6c39d8 () {
  const reflex___state____state__warframe_reflex___state____calculator_state = useContext(StateContexts.reflex___state____state__warframe_reflex___state____calculator_state)



  return (
    jsx(RadixThemesTable.Body,{},Array.prototype.map.call(reflex___state____state__warframe_reflex___state____calculator_state.damage_result_rows_rx_state_ ?? [],((row_rx_state_,index_0e1dbe9a52ab7a8c57217ff69aca0fd4)=>(jsx(RadixThemesTable.Row,{key:index_0e1dbe9a52ab7a8c57217ff69aca0fd4},jsx(RadixThemesTable.RowHeaderCell,{},row_rx_state_?.["damage_type"]),jsx(RadixThemesTable.Cell,{},row_rx_state_?.["damage"]),jsx(RadixThemesTable.Cell,{},row_rx_state_?.["direct_weight"]),jsx(RadixThemesTable.Cell,{},row_rx_state_?.["explosion_weight"]),jsx(RadixThemesTable.Cell,{},row_rx_state_?.["proc_chance"]))))))
  )
}


function Fragment_3adc8207e745259fe80231275a72b944 () {
  const reflex___state____state__warframe_reflex___state____calculator_state = useContext(StateContexts.reflex___state____state__warframe_reflex___state____calculator_state)



  return (
    jsx(Fragment,{},(reflex___state____state__warframe_reflex___state____calculator_state.melee_weapon_rx_state_?(jsx(Fragment,{},jsx(RadixThemesTable.Root,{css:({ ["width"] : "100%" }),variant:"surface"},jsx(RadixThemesTable.Header,{},jsx(RadixThemesTable.Row,{},jsx(RadixThemesTable.ColumnHeaderCell,{},"Damage Type"),jsx(RadixThemesTable.ColumnHeaderCell,{},"Damage"),jsx(RadixThemesTable.ColumnHeaderCell,{},"Weight"),jsx(RadixThemesTable.ColumnHeaderCell,{},"Proc Chance"))),jsx(Table__body_e8f64911eaa72ab5b8579a7197e8a35c,{},)))):(jsx(Fragment,{},jsx(RadixThemesTable.Root,{css:({ ["width"] : "100%" }),variant:"surface"},jsx(RadixThemesTable.Header,{},jsx(RadixThemesTable.Row,{},jsx(RadixThemesTable.ColumnHeaderCell,{},"Damage Type"),jsx(RadixThemesTable.ColumnHeaderCell,{},"Damage"),jsx(RadixThemesTable.ColumnHeaderCell,{},"Direct Hit Weight"),jsx(RadixThemesTable.ColumnHeaderCell,{},"Explosion Weight"),jsx(RadixThemesTable.ColumnHeaderCell,{},"Proc Chance"))),jsx(Table__body_8721add4af4bc1e4854717eadb6c39d8,{},))))))
  )
}


function Flex_1fcc26d6b4d88a54ab55c4edb39ab3df () {
  const reflex___state____state__warframe_reflex___state____calculator_state = useContext(StateContexts.reflex___state____state__warframe_reflex___state____calculator_state)



  return (
    jsx(RadixThemesFlex,{align:"start",className:"rx-Stack",css:({ ["width"] : "100%", ["gap"] : "1" }),direction:"column",gap:"3"},Array.prototype.map.call(reflex___state____state__warframe_reflex___state____calculator_state.contribution_result_rows_rx_state_ ?? [],((row_rx_state_,index_134d905f168853dc27e59410cdca0485)=>(jsx(RadixThemesFlex,{align:"center",className:"rx-Stack contribution-row",css:({ ["width"] : "100%" }),direction:"row",key:index_134d905f168853dc27e59410cdca0485,gap:"3"},jsx(RadixThemesText,{as:"p"},row_rx_state_?.["name"]),jsx(RadixThemesFlex,{css:({ ["flex"] : 1, ["justifySelf"] : "stretch", ["alignSelf"] : "stretch" })},),jsx(RadixThemesText,{as:"p",className:"preview-value"},row_rx_state_?.["value"]))))))
  )
}


function Fragment_1634bdf63c1b95be152761a4bee555ae () {
  const reflex___state____state__warframe_reflex___state____calculator_state = useContext(StateContexts.reflex___state____state__warframe_reflex___state____calculator_state)



  return (
    jsx(Fragment,{},((reflex___state____state__warframe_reflex___state____calculator_state.contribution_result_rows_rx_state_.length > 0)?(jsx(Fragment,{},jsx(Flex_1fcc26d6b4d88a54ab55c4edb39ab3df,{},))):(jsx(Fragment,{},jsx(RadixThemesText,{as:"p",className:"empty-text"},"No upgrade contributions.")))))
  )
}


function Prismasynclight_f2f308eb4ec487f2d0095c0f43761d1c () {
  const { resolvedColorMode } = useContext(ColorModeContext)
const reflex___state____state__warframe_reflex___state____calculator_state = useContext(StateContexts.reflex___state____state__warframe_reflex___state____calculator_state)



  return (
    jsx(SyntaxHighlighter,{children:reflex___state____state__warframe_reflex___state____calculator_state.result_summary_rx_state_,css:({ ["width"] : "100%" }),language:"log",style:((resolvedColorMode?.valueOf?.() === "light"?.valueOf?.()) ? oneLight : oneDark),wrapLongLines:true},)
  )
}


function Prismasynclight_c3931a1e6a5b4684d299f1c1d716b5e2 () {
  const { resolvedColorMode } = useContext(ColorModeContext)
const reflex___state____state__warframe_reflex___state____calculator_state = useContext(StateContexts.reflex___state____state__warframe_reflex___state____calculator_state)



  return (
    jsx(SyntaxHighlighter,{children:reflex___state____state__warframe_reflex___state____calculator_state.result_contribution_summary_rx_state_,css:({ ["width"] : "100%" }),language:"log",style:((resolvedColorMode?.valueOf?.() === "light"?.valueOf?.()) ? oneLight : oneDark),wrapLongLines:true},)
  )
}


function Fragment_ec9a3bfa62f889ac944b6c57d01d1ed1 () {
  const reflex___state____state__warframe_reflex___state____calculator_state = useContext(StateContexts.reflex___state____state__warframe_reflex___state____calculator_state)



  return (
    jsx(Fragment,{},(!(reflex___state____state__warframe_reflex___state____calculator_state.has_error_rx_state_)?(jsx(Fragment,{},jsx(RadixThemesBox,{className:"panel"},jsx(RadixThemesText,{as:"p",className:"empty-text"},"Preparing calculator results\u2026")))):(jsx(Fragment,{},))))
  )
}


function Fragment_cf56ba28d5ff48f91029f1693f7ed87b () {
  const reflex___state____state__warframe_reflex___state____calculator_state = useContext(StateContexts.reflex___state____state__warframe_reflex___state____calculator_state)



  return (
    jsx(Fragment,{},(reflex___state____state__warframe_reflex___state____calculator_state.result_ready_rx_state_?(jsx(Fragment,{},jsx(RadixThemesFlex,{align:"start",className:"rx-Stack",css:({ ["width"] : "100%", ["gap"] : "4" }),direction:"column",gap:"3"},jsx(Fragment_aea0fecb057b689ff889ff463e5cd0e0,{},),jsx(RadixThemesBox,{className:"panel"},jsx(RadixThemesTabs.Root,{css:({ ["&[data-orientation='vertical']"] : ({ ["display"] : "flex" }), ["width"] : "100%" }),defaultValue:"damage"},jsx(RadixThemesTabs.List,{css:({ ["&[data-orientation='vertical']"] : ({ ["display"] : "block", ["boxShadow"] : "inset -1px 0 0 0 var(--gray-a5)" }) })},jsx(RadixThemesTabs.Trigger,{css:({ ["&[data-orientation='vertical']"] : ({ ["width"] : "100%" }) }),value:"damage"},"Damage Distribution"),jsx(RadixThemesTabs.Trigger,{css:({ ["&[data-orientation='vertical']"] : ({ ["width"] : "100%" }) }),value:"contributions"},"Contributions"),jsx(RadixThemesTabs.Trigger,{css:({ ["&[data-orientation='vertical']"] : ({ ["width"] : "100%" }) }),value:"summary"},"Text Summary")),jsx(RadixThemesTabs.Content,{css:({ ["&[data-orientation='vertical']"] : ({ ["width"] : "100%", ["margin"] : null }), ["paddingTop"] : "1rem" }),value:"damage"},jsx(RadixThemesBox,{css:({ ["width"] : "100%", ["overflowX"] : "auto" })},jsx(Fragment_3adc8207e745259fe80231275a72b944,{},))),jsx(RadixThemesTabs.Content,{css:({ ["&[data-orientation='vertical']"] : ({ ["width"] : "100%", ["margin"] : null }), ["paddingTop"] : "1rem" }),value:"contributions"},jsx(Fragment_1634bdf63c1b95be152761a4bee555ae,{},)),jsx(RadixThemesTabs.Content,{css:({ ["&[data-orientation='vertical']"] : ({ ["width"] : "100%", ["margin"] : null }), ["paddingTop"] : "1rem" }),value:"summary"},jsx(RadixThemesFlex,{align:"start",className:"rx-Stack",css:({ ["width"] : "100%", ["gap"] : "3" }),direction:"column",gap:"3"},jsx(RadixThemesText,{as:"p",className:"card-title"},"Weapon Summary"),jsx(Prismasynclight_f2f308eb4ec487f2d0095c0f43761d1c,{},),jsx(RadixThemesText,{as:"p",className:"card-title"},"Upgrade Contributions"),jsx(Prismasynclight_c3931a1e6a5b4684d299f1c1d716b5e2,{},)))))))):(jsx(Fragment_ec9a3bfa62f889ac944b6c57d01d1ed1,{},))))
  )
}


export default function Component() {





  return (
    jsx(Fragment,{},jsx(RadixThemesBox,{className:"page-shell"},jsx(RadixThemesFlex,{align:"start",className:"rx-Stack",css:({ ["width"] : "100%", ["gap"] : "7" }),direction:"column",gap:"3"},jsx(RadixThemesFlex,{align:"center",className:"rx-Stack app-header",css:({ ["width"] : "100%" }),direction:"row",gap:"3"},jsx(RadixThemesFlex,{align:"start",className:"rx-Stack",css:({ ["gap"] : "1" }),direction:"column",gap:"3"},jsx(RadixThemesHeading,{size:"7"},"Warframe Damage Calculator"),jsx(RadixThemesText,{as:"p",className:"header-subtitle"},"Configure a weapon, build, and external buffs with deterministic DPH/DPS calculations.")),jsx(RadixThemesFlex,{css:({ ["flex"] : 1, ["justifySelf"] : "stretch", ["alignSelf"] : "stretch" })},),jsx(RadixThemesBadge,{size:"2",variant:"soft"},"Reflex")),jsx(RadixAccordionRoot,{className:"read-me",collapsible:true,css:({ ["borderRadius"] : "var(--radius-4)", ["boxShadow"] : "0 2px 10px var(--black-a1)", ["&[data-variant='classic']"] : ({ ["backgroundColor"] : "var(--accent-9)", ["boxShadow"] : "0 2px 10px var(--black-a4)" }), ["&[data-variant='soft']"] : ({ ["backgroundColor"] : "var(--accent-3)" }), ["&[data-variant='outline']"] : ({ ["border"] : "1px solid var(--accent-6)", ["--divider-px"] : "1px" }), ["&[data-variant='surface']"] : ({ ["border"] : "1px solid var(--accent-6)", ["backgroundColor"] : "var(--accent-surface)", ["--divider-px"] : "1px" }), ["&[data-variant='ghost']"] : ({ ["backgroundColor"] : "none", ["boxShadow"] : "None" }), ["--animation-duration"] : (250+"ms"), ["--animation-easing"] : "cubic-bezier(0.87, 0, 0.13, 1)", ["width"] : "100%" }),"data-variant":"classic",type:"single"},jsx(RadixAccordionItem,{className:"AccordionItem",css:({ ["overflow"] : "hidden", ["width"] : "100%", ["marginTop"] : "1px", ["borderTop"] : "var(--divider-px) solid var(--gray-a6)", ["&:first-child"] : ({ ["marginTop"] : 0, ["borderTop"] : 0, ["borderTopLeftRadius"] : "var(--radius-4)", ["borderTopRightRadius"] : "var(--radius-4)" }), ["&:last-child"] : ({ ["borderBottomLeftRadius"] : "var(--radius-4)", ["borderBottomRightRadius"] : "var(--radius-4)" }), ["&:focus-within"] : ({ ["position"] : "relative", ["zIndex"] : 1 }), ["&:first-child[data-variant='ghost'], *:where([data-variant='ghost']) &:first-child"] : ({ ["borderRadius"] : 0, ["borderTop"] : "var(--divider-px) solid var(--gray-a6)" }), ["&:last-child[data-variant='ghost'], *:where([data-variant='ghost']) &:last-child"] : ({ ["borderRadius"] : 0, ["borderBottom"] : "var(--divider-px) solid var(--gray-a6)" }) }),value:"read-me"},jsx(RadixAccordionHeader,{className:"AccordionHeader",css:({ ["display"] : "flex", ["margin"] : "0" })},jsx(RadixAccordionTrigger,{className:"AccordionTrigger",css:({ ["color"] : "var(--accent-11)", ["fontSize"] : "1.1em", ["lineHeight"] : 1, ["justifyContent"] : "space-between", ["alignItems"] : "center", ["flex"] : 1, ["display"] : "flex", ["padding"] : "var(--space-3) var(--space-4)", ["width"] : "100%", ["boxShadow"] : "0 var(--divider-px) 0 var(--gray-a6)", ["&[data-state='open'] > .AccordionChevron"] : ({ ["transform"] : "rotate(180deg)" }), ["&:hover"] : ({ ["backgroundColor"] : "var(--accent-4)" }), ["& > .AccordionChevron"] : ({ ["transition"] : "transform var(--animation-duration) var(--animation-easing)" }), ["&[data-variant='classic'], *:where([data-variant='classic']) &"] : ({ ["color"] : "var(--accent-contrast)", ["&:hover"] : ({ ["backgroundColor"] : "var(--accent-10)" }), ["& > .AccordionChevron"] : ({ ["color"] : "var(--accent-contrast)" }) }), ["background"] : "none", ["border"] : "none" })},jsx(RadixAccordionHeader,{className:"AccordionHeader",css:({ ["display"] : "flex", ["margin"] : "0" })},jsx(RadixAccordionTrigger,{className:"AccordionTrigger",css:({ ["color"] : "var(--accent-11)", ["fontSize"] : "1.1em", ["lineHeight"] : 1, ["justifyContent"] : "space-between", ["alignItems"] : "center", ["flex"] : 1, ["display"] : "flex", ["padding"] : "var(--space-3) var(--space-4)", ["width"] : "100%", ["boxShadow"] : "0 var(--divider-px) 0 var(--gray-a6)", ["&[data-state='open'] > .AccordionChevron"] : ({ ["transform"] : "rotate(180deg)" }), ["&:hover"] : ({ ["backgroundColor"] : "var(--accent-4)" }), ["& > .AccordionChevron"] : ({ ["transition"] : "transform var(--animation-duration) var(--animation-easing)" }), ["&[data-variant='classic'], *:where([data-variant='classic']) &"] : ({ ["color"] : "var(--accent-contrast)", ["&:hover"] : ({ ["backgroundColor"] : "var(--accent-10)" }), ["& > .AccordionChevron"] : ({ ["color"] : "var(--accent-contrast)" }) }), ["background"] : "none", ["border"] : "none" })},jsx(RadixThemesFlex,{align:"start",className:"rx-Stack",css:({ ["width"] : "100%" }),direction:"row",gap:"3"},jsx(RadixThemesText,{as:"p"},"Read Me"),jsx(RadixThemesFlex,{css:({ ["flex"] : 1, ["justifySelf"] : "stretch", ["alignSelf"] : "stretch" })},),jsx(LucideChevronDown,{className:"AccordionChevron"},)))),jsx(LucideChevronDown,{className:"AccordionChevron"},))),jsx(RadixAccordionContent,{className:"AccordionContent",css:({ ["overflow"] : "hidden", ["color"] : "var(--accent-11)", ["paddingInlineStart"] : "var(--space-4)", ["paddingInlineEnd"] : "var(--space-4)", ["&:before, &:after"] : ({ ["content"] : "' '", ["display"] : "block", ["height"] : "var(--space-3)" }), ["&[data-state='open']"] : ({ ["animation"] : (keyframes({ from: { height: 0 }, to: { height: "var(--radix-accordion-content-height)" } })+" var(--animation-duration) var(--animation-easing)") }), ["&[data-state='closed']"] : ({ ["animation"] : (keyframes({ from: { height: "var(--radix-accordion-content-height)" }, to: { height: 0 } })+" var(--animation-duration) var(--animation-easing)") }), ["&[data-variant='classic'], *:where([data-variant='classic']) &"] : ({ ["color"] : "var(--accent-contrast)" }) })},jsx(RadixAccordionContent,{className:"AccordionContent",css:({ ["overflow"] : "hidden", ["color"] : "var(--accent-11)", ["paddingInlineStart"] : "var(--space-4)", ["paddingInlineEnd"] : "var(--space-4)", ["&:before, &:after"] : ({ ["content"] : "' '", ["display"] : "block", ["height"] : "var(--space-3)" }), ["&[data-state='open']"] : ({ ["animation"] : (keyframes({ from: { height: 0 }, to: { height: "var(--radix-accordion-content-height)" } })+" var(--animation-duration) var(--animation-easing)") }), ["&[data-state='closed']"] : ({ ["animation"] : (keyframes({ from: { height: "var(--radix-accordion-content-height)" }, to: { height: 0 } })+" var(--animation-duration) var(--animation-easing)") }), ["&[data-variant='classic'], *:where([data-variant='classic']) &"] : ({ ["color"] : "var(--accent-contrast)" }) })},jsx(RadixThemesFlex,{align:"start",className:"rx-Stack",css:({ ["gap"] : "3", ["width"] : "100%", ["paddingTop"] : "0.5rem" }),direction:"column",gap:"3"},jsx(RadixThemesHeading,{size:"4"},"Disclaimer"),jsx(RadixThemesText,{as:"p"},"This interface is a companion for the warframe_damage_calculator Python library. The library remains the source of truth for all damage calculations."),jsx(RadixThemesHeading,{size:"4"},"Instructions"),jsx(RadixThemesText,{as:"p"},"Select a weapon type and weapon, configure custom base stats when needed, fill the eight mod slots plus Exilus and Arcane, add external buffs, then inspect the live results."),jsx(RadixThemesHeading,{size:"4"},"Notes"),jsx(RadixThemesText,{as:"p"},"Percentage bonuses use decimal values: +75% is entered as 0.75. Multiplicative bonuses use the bonus over base: \u00d71.30 is entered as 0.30."),jsx(RadixThemesFlex,{align:"start",className:"rx-Stack",css:({ ["gap"] : "4" }),direction:"row",gap:"3",wrap:"wrap"},jsx(RadixThemesLink,{asChild:true,css:({ ["&:hover"] : ({ ["color"] : "var(--accent-8)" }) })},jsx(ReactRouterLink,{target:(true ? "_blank" : ""),to:"https://github.com/AAAA0001/warframe-damage-calculator-web"},"Web app source")),jsx(RadixThemesLink,{asChild:true,css:({ ["&:hover"] : ({ ["color"] : "var(--accent-8)" }) })},jsx(ReactRouterLink,{target:(true ? "_blank" : ""),to:"https://github.com/AAAA0001/warframe-damage-calculator"},"Python library")))))))),jsx(RadixThemesFlex,{align:"start",className:"rx-Stack",css:({ ["width"] : "100%", ["gap"] : "3" }),direction:"column",gap:"3"},jsx(RadixThemesFlex,{align:"start",className:"rx-Stack",css:({ ["gap"] : "1", ["width"] : "100%" }),direction:"column",gap:"3"},jsx(RadixThemesHeading,{size:"6"},"Weapon"),jsx(Fragment,{},(true?(jsx(Fragment,{},jsx(RadixThemesText,{as:"p",className:"section-subtitle"},"Choose a database weapon or define a custom one."))):(jsx(Fragment,{},))))),jsx(RadixThemesBox,{className:"panel"},jsx(RadixThemesFlex,{align:"start",className:"rx-Stack",css:({ ["width"] : "100%", ["gap"] : "5" }),direction:"column",gap:"3"},jsx(RadixThemesGrid,{className:"form-grid form-grid-2",columns:({ ["initial"] : "1", ["md"] : "2" }),css:({ ["gap"] : "4", ["width"] : "100%" })},jsx(RadixThemesFlex,{align:"start",className:"rx-Stack",css:({ ["gap"] : "1", ["width"] : "100%" }),direction:"column",gap:"3"},jsx(RadixThemesText,{as:"p",className:"field-label"},"Weapon Type"),jsx(Select__root_0b867d07f7089935bcae2ccfe2884636,{},)),jsx(RadixThemesFlex,{align:"start",className:"rx-Stack",css:({ ["gap"] : "1", ["width"] : "100%" }),direction:"column",gap:"3"},jsx(RadixThemesText,{as:"p",className:"field-label"},"Weapon"),jsx(Select__root_4b29509caa1269fca3cd82330720fee9,{},))),jsx(Fragment_44436c3c26f609346484b43b31c366bb,{},)))),jsx(RadixThemesFlex,{align:"start",className:"rx-Stack",css:({ ["width"] : "100%", ["gap"] : "4" }),direction:"column",gap:"3"},jsx(RadixThemesFlex,{align:"start",className:"rx-Stack",css:({ ["gap"] : "1", ["width"] : "100%" }),direction:"column",gap:"3"},jsx(RadixThemesHeading,{size:"6"},"Upgrades"),jsx(Fragment,{},(true?(jsx(Fragment,{},jsx(RadixThemesText,{as:"p",className:"section-subtitle"},"Eight normal mod slots, one Arcane slot, one Exilus slot, and external buffs."))):(jsx(Fragment,{},))))),jsx(RadixThemesBox,{className:"slot-grid-scroll",css:({ ["width"] : "100%" })},jsx(RadixThemesBox,{className:"slot-grid"},jsx(RadixThemesBox,{className:"slot-card"},jsx(RadixThemesFlex,{align:"start",className:"rx-Stack",css:({ ["width"] : "100%", ["gap"] : "3" }),direction:"column",gap:"3"},jsx(RadixThemesFlex,{align:"center",className:"rx-Stack",css:({ ["width"] : "100%" }),direction:"row",gap:"3"},jsx(RadixThemesText,{as:"p",className:"card-title"},"Mod 1"),jsx(RadixThemesFlex,{css:({ ["flex"] : 1, ["justifySelf"] : "stretch", ["alignSelf"] : "stretch" })},),jsx(Badge_e5892c5677fa1c50a593e45b62fa0c27,{},)),jsx(Select__root_bc8fbbbfa613543ced82d007de8c255a,{},),jsx(Fragment_7e4f4d37efb125abf1e629b89a63993a,{},))),jsx(RadixThemesBox,{className:"slot-card"},jsx(RadixThemesFlex,{align:"start",className:"rx-Stack",css:({ ["width"] : "100%", ["gap"] : "3" }),direction:"column",gap:"3"},jsx(RadixThemesFlex,{align:"center",className:"rx-Stack",css:({ ["width"] : "100%" }),direction:"row",gap:"3"},jsx(RadixThemesText,{as:"p",className:"card-title"},"Mod 2"),jsx(RadixThemesFlex,{css:({ ["flex"] : 1, ["justifySelf"] : "stretch", ["alignSelf"] : "stretch" })},),jsx(Badge_a97901c07a3a98a858665408b9134a2d,{},)),jsx(Select__root_b6d728b6bb97202ae0fa1e8c9610183b,{},),jsx(Fragment_566b4d3a78f405e6f70893fda9071c45,{},))),jsx(RadixThemesBox,{className:"slot-card"},jsx(RadixThemesFlex,{align:"start",className:"rx-Stack",css:({ ["width"] : "100%", ["gap"] : "3" }),direction:"column",gap:"3"},jsx(RadixThemesFlex,{align:"center",className:"rx-Stack",css:({ ["width"] : "100%" }),direction:"row",gap:"3"},jsx(RadixThemesText,{as:"p",className:"card-title"},"Mod 3"),jsx(RadixThemesFlex,{css:({ ["flex"] : 1, ["justifySelf"] : "stretch", ["alignSelf"] : "stretch" })},),jsx(Badge_6a03a4e6b5ac6034bd9e918878b6d460,{},)),jsx(Select__root_f745a1f0dc84f80c24bcb0fe8cacd09a,{},),jsx(Fragment_ac0c352ad312f583f91e22b28de07a23,{},))),jsx(RadixThemesBox,{className:"slot-card"},jsx(RadixThemesFlex,{align:"start",className:"rx-Stack",css:({ ["width"] : "100%", ["gap"] : "3" }),direction:"column",gap:"3"},jsx(RadixThemesFlex,{align:"center",className:"rx-Stack",css:({ ["width"] : "100%" }),direction:"row",gap:"3"},jsx(RadixThemesText,{as:"p",className:"card-title"},"Mod 4"),jsx(RadixThemesFlex,{css:({ ["flex"] : 1, ["justifySelf"] : "stretch", ["alignSelf"] : "stretch" })},),jsx(Badge_de4591d81d49141ed8b1977917dbd4c4,{},)),jsx(Select__root_338de6cda39202a4fb0acc86b51c9331,{},),jsx(Fragment_11fe049af6ea1345559ed00f89841913,{},))),jsx(RadixThemesBox,{className:"slot-card"},jsx(RadixThemesFlex,{align:"start",className:"rx-Stack",css:({ ["width"] : "100%", ["gap"] : "3" }),direction:"column",gap:"3"},jsx(RadixThemesFlex,{align:"center",className:"rx-Stack",css:({ ["width"] : "100%" }),direction:"row",gap:"3"},jsx(RadixThemesText,{as:"p",className:"card-title"},"Arcane"),jsx(RadixThemesFlex,{css:({ ["flex"] : 1, ["justifySelf"] : "stretch", ["alignSelf"] : "stretch" })},),jsx(Badge_6b974f8a0b178d20d5c837243116943b,{},)),jsx(Select__root_5a3f33e973dacefa80adf7583ad3ff8e,{},),jsx(Fragment_f58191500462d3a1751a52fc92c1bc40,{},))),jsx(RadixThemesBox,{className:"slot-card"},jsx(RadixThemesFlex,{align:"start",className:"rx-Stack",css:({ ["width"] : "100%", ["gap"] : "3" }),direction:"column",gap:"3"},jsx(RadixThemesFlex,{align:"center",className:"rx-Stack",css:({ ["width"] : "100%" }),direction:"row",gap:"3"},jsx(RadixThemesText,{as:"p",className:"card-title"},"Mod 5"),jsx(RadixThemesFlex,{css:({ ["flex"] : 1, ["justifySelf"] : "stretch", ["alignSelf"] : "stretch" })},),jsx(Badge_648b7852ad11ffe7b4c434a5772a62e9,{},)),jsx(Select__root_8c868c5b431b9090cd1ad0debe50a16f,{},),jsx(Fragment_4bbd69e76ede1f24b898d40810c0f05b,{},))),jsx(RadixThemesBox,{className:"slot-card"},jsx(RadixThemesFlex,{align:"start",className:"rx-Stack",css:({ ["width"] : "100%", ["gap"] : "3" }),direction:"column",gap:"3"},jsx(RadixThemesFlex,{align:"center",className:"rx-Stack",css:({ ["width"] : "100%" }),direction:"row",gap:"3"},jsx(RadixThemesText,{as:"p",className:"card-title"},"Mod 6"),jsx(RadixThemesFlex,{css:({ ["flex"] : 1, ["justifySelf"] : "stretch", ["alignSelf"] : "stretch" })},),jsx(Badge_43191d40e80b8bba12520da6d407d0db,{},)),jsx(Select__root_607090528477ce11ec5b96c796fb1e89,{},),jsx(Fragment_da9cbea26663da96f0112422bb6c7c66,{},))),jsx(RadixThemesBox,{className:"slot-card"},jsx(RadixThemesFlex,{align:"start",className:"rx-Stack",css:({ ["width"] : "100%", ["gap"] : "3" }),direction:"column",gap:"3"},jsx(RadixThemesFlex,{align:"center",className:"rx-Stack",css:({ ["width"] : "100%" }),direction:"row",gap:"3"},jsx(RadixThemesText,{as:"p",className:"card-title"},"Mod 7"),jsx(RadixThemesFlex,{css:({ ["flex"] : 1, ["justifySelf"] : "stretch", ["alignSelf"] : "stretch" })},),jsx(Badge_de4494a6811cc0c45c6d23690da1c4bc,{},)),jsx(Select__root_363ac76ac3fac0b169b905524d5a092d,{},),jsx(Fragment_e9e9380e1bb00ab0ca7394dc1e0cecd4,{},))),jsx(RadixThemesBox,{className:"slot-card"},jsx(RadixThemesFlex,{align:"start",className:"rx-Stack",css:({ ["width"] : "100%", ["gap"] : "3" }),direction:"column",gap:"3"},jsx(RadixThemesFlex,{align:"center",className:"rx-Stack",css:({ ["width"] : "100%" }),direction:"row",gap:"3"},jsx(RadixThemesText,{as:"p",className:"card-title"},"Mod 8"),jsx(RadixThemesFlex,{css:({ ["flex"] : 1, ["justifySelf"] : "stretch", ["alignSelf"] : "stretch" })},),jsx(Badge_15dfe03d30c8421c3728447ff3b853cc,{},)),jsx(Select__root_e5e78961d9e0d27418c5718495b402cb,{},),jsx(Fragment_31a778764de21a99e847ebdc51f08e07,{},))),jsx(RadixThemesBox,{className:"slot-card"},jsx(RadixThemesFlex,{align:"start",className:"rx-Stack",css:({ ["width"] : "100%", ["gap"] : "3" }),direction:"column",gap:"3"},jsx(RadixThemesFlex,{align:"center",className:"rx-Stack",css:({ ["width"] : "100%" }),direction:"row",gap:"3"},jsx(RadixThemesText,{as:"p",className:"card-title"},"Exilus"),jsx(RadixThemesFlex,{css:({ ["flex"] : 1, ["justifySelf"] : "stretch", ["alignSelf"] : "stretch" })},),jsx(Badge_6dea4a56dc58fbf481d7731c19dbd331,{},)),jsx(Select__root_e99e6b3d9948c86064153089032ef7b7,{},),jsx(Fragment_ce28823ad6aed14e3ae137c9e968e3f9,{},))))),jsx(RadixThemesFlex,{align:"start",className:"rx-Stack",css:({ ["gap"] : "3", ["width"] : "100%" }),direction:"column",gap:"3"},jsx(RadixThemesHeading,{size:"4"},"External Buffs"),jsx(RadixThemesBox,{className:"panel"},jsx(RadixThemesFlex,{align:"start",className:"rx-Stack",css:({ ["width"] : "100%", ["gap"] : "3" }),direction:"column",gap:"3"},jsx(RadixThemesGrid,{columns:"minmax(0, 1fr) 32px",css:({ ["columnGap"] : "8px", ["width"] : "100%" })},jsx(Select__root_8d758698bfde90af9cc3b07a7902b9a5,{},),jsx(Button_ccd775f90ae81b7a376e2a14287d63a4,{},)),jsx(Fragment_4642706f68dc54964a6c439554e4dbc9,{},))))),jsx(RadixThemesFlex,{align:"start",className:"rx-Stack",css:({ ["width"] : "100%", ["gap"] : "3" }),direction:"column",gap:"3"},jsx(RadixThemesFlex,{align:"start",className:"rx-Stack",css:({ ["gap"] : "1", ["width"] : "100%" }),direction:"column",gap:"3"},jsx(RadixThemesHeading,{size:"6"},"Results"),jsx(Fragment,{},(true?(jsx(Fragment,{},jsx(RadixThemesText,{as:"p",className:"section-subtitle"},"Updated automatically whenever the build changes."))):(jsx(Fragment,{},))))),jsx(Fragment_ae1710cba5a9b70e84f39fb8665c58ec,{},),jsx(Fragment_cf56ba28d5ff48f91029f1693f7ed87b,{},)))),jsx("title",{},"Warframe Damage Calculator"),jsx("meta",{content:"A Reflex interface for warframe_damage_calculator.",name:"description"},),jsx("meta",{content:"favicon.ico",property:"og:image"},))
  )
}