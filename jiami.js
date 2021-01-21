var $_chars = 'ABCDEFGHJKMNPQRSTWXYZabcdefhijkmnprstwxyz2345678';
var _chars_len = $_chars.length;

function _rds(len) {
    //randomstring参数:64,16
    var retStr = '';
    for (i = 0; i < len; i++) {
        retStr += $_chars.charAt(Math.floor(Math.random() * _chars_len));
    }
    return retStr;
}

function _gas(data, key0, iv0) {
    //_rds(64) + data, _p1, _rds(16)
    key0 = key0.replace(/(^\s+)|(\s+$)/g, "");
    var key = CryptoJS.enc.Utf8.parse(key0);
    var iv = CryptoJS.enc.Utf8.parse(iv0);
    var encrypted = CryptoJS.AES.encrypt(data, key, {iv: iv, mode: CryptoJS.mode.CBC, padding: CryptoJS.pad.Pkcs7});
    return encrypted.toString();
}


function encryptAES(data, _p1) {
    //参数:密码,OdkJwOCwX4snz9CD
    if (!_p1) {
        return data;
    }
    var encrypted = _gas(_rds(64) + data, _p1, _rds(16));
    return encrypted;
}

function _etd2(_p0, _p1) {
    //参数:密码,OdkJwOCwX4snz9CD
    var _p2 = encryptAES(_p0, _p1);
    return _p2;

}



//OdkJwOCwX4snz9CD




//--------------------------------------------//
