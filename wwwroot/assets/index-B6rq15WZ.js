/**
 * Copyright (C) 2003-present CompatibL. All rights reserved.
 * This file contains valuable trade secrets and may be copied, stored, used,
 * or distributed only in compliance with the terms of a written commercial
 * license from CompatibL and with the inclusion of this copyright notice.
 */
import{g as u}from"./react-BmNO_Eks.js";import{s as l,r as g}from"./index-DrTjU7Oy.js";function h(i,o){for(var f=0;f<o.length;f++){const r=o[f];if(typeof r!="string"&&!Array.isArray(r)){for(const e in r)if(e!=="default"&&!(e in i)){const n=Object.getOwnPropertyDescriptor(r,e);n&&Object.defineProperty(i,e,n.get?n:{enumerable:!0,get:()=>r[e]})}}}return Object.freeze(Object.defineProperty(i,Symbol.toStringTag,{value:"Module"}))}var c={exports:{}};(function(i){var o=l,f=g,r=i.exports;for(var e in o)o.hasOwnProperty(e)&&(r[e]=o[e]);r.request=function(t,s){return t=n(t),o.request.call(this,t,s)},r.get=function(t,s){return t=n(t),o.get.call(this,t,s)};function n(t){if(typeof t=="string"&&(t=f.parse(t)),t.protocol||(t.protocol="https:"),t.protocol!=="https:")throw new Error('Protocol "'+t.protocol+'" not supported. Expected "https:"');return t}})(c);var p=c.exports;const d=u(p),y=h({__proto__:null,default:d},[p]);export{y as i};
