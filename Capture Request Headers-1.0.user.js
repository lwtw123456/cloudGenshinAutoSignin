// ==UserScript==
// @name         Capture Request Headers
// @namespace    http://tampermonkey.net/
// @version      1.0
// @description  捕获发送请求的完整header
// @author       You
// @match        https://ys.mihoyo.com/*
// @grant        unsafeWindow
// @grant        GM_xmlhttpRequest
// @run-at       document-start
// ==/UserScript==

(function() {
    'use strict';

    const TARGET_URLS = [
        '/hk4e_cg_cn/gamer/api/getUIConfig',
        '/hk4e_cg_cn/gamer/api/login'
    ];

    function isTargetUrl(url) {
        return TARGET_URLS.some(t => url.includes(t));
    }

    function shouldOutput(headers) {
        const token = headers['x-rpc-combo_token'];
        if (!token) return false;

        const ctMatch = token.match(/ct=([^;]*)/);
        if (!ctMatch || !ctMatch[1]) return false;

        return true;
    }

    const originalXHROpen = unsafeWindow.XMLHttpRequest.prototype.open;
    const originalXHRSetRequestHeader = unsafeWindow.XMLHttpRequest.prototype.setRequestHeader;
    const originalXHRSend = unsafeWindow.XMLHttpRequest.prototype.send;

    unsafeWindow.XMLHttpRequest.prototype.open = function(method, url, ...args) {
        this._url = url;
        this._headers = {};
        return originalXHROpen.apply(this, [method, url, ...args]);
    };

    unsafeWindow.XMLHttpRequest.prototype.setRequestHeader = function(name, value) {
        if (this._headers) this._headers[name] = value;
        return originalXHRSetRequestHeader.apply(this, [name, value]);
    };

    unsafeWindow.XMLHttpRequest.prototype.send = function(body) {
        const result = originalXHRSend.apply(this, [body]);

        if (this._url && isTargetUrl(this._url) && shouldOutput(this._headers)) {
            GM_xmlhttpRequest({
                method: "POST",
                url: "http://127.0.0.1:5000/push",
                headers: {"Content-Type": "application/json"},
                data: JSON.stringify({ headers: this._headers })
            });
        }

        return result;
    };
})();