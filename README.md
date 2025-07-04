# Taipei Day Trip

## 目錄
- [網站簡介 Introduction](#網站簡介-introduction)
- [使用技術 Techniques](#使用技術-techniques)
- [網站功能 Features](#網站功能-features)
- [聯絡資訊 Contact](#聯絡資訊-contact)

## 網站簡介 Introduction
本專案為旅遊電商網站，以政府公開資料平台之台北景點作為資料來源。採用前後端分離開發，前端透過 AJAX 非同步呼叫 RESTful API，取得公開景點資訊。使用者可瀏覽景點卡片，點擊查看詳細資訊，並在註冊登入後，透過 TapPay SDK 安全地預訂行程並完成付款。會員亦可在帳戶頁面查詢自己的訂單紀錄。

網址: http://13.228.226.220:8000/
* 測試帳號：test@test.com
* 密碼：123456
* 信用卡測試
    * 卡號：4242-4242-4242-4242
    * 效期：任一未過期的年月（ex: 12/30）
    * CCV：任３位數字



## 使用技術 Techniques
* 前端技術
    * HTML5 / CSS3 / JavaScript
        * Infinite Scroll & Lazy Loading
        * Carousel
        * Responsive Web Design (RWD)
        * Horizontal scrollable MRT quick‑filter bar (可依捷運站點快速篩選景點)
* 後端 / API 技術：
    * Python 
    * FastAPI
* 資料庫
    * MySQL（儲存會員資料、訂單資訊與景點資料）
* 會員系統
    * 前端：原生JavaScript + Fetch API，登入後將 JWT 儲存在 localStorage
    * 後端：FastAPI + MySQL
        * FastAPI 建立帳號註冊、登入驗證 API，使用 JWT 驗證存取權限
        * 資料儲存：使用 MySQL 建立使用者資料表，儲存使用者資訊
        * 功能：支援帳號驗證、歷史訂單查詢
* 付款系統
    * 第三方金流服務 TapPay SDK
* 網站部署
    * AWS EC2
* 使用 Git/GitHub 進行版本控管，每週完成階段性任務後，向Reviewer發送 Pull Request，取得同意後將develop分支合併到main分支，並將程式碼同步到AWS EC2更新網站。



## 網站功能 Features
(1) 首頁瀏覽  
使用Javascript Intersection Observer API + Fetch API  實踐 Lazy Loading 和 Infinite Scroll，滾動載入景點卡片，降低瀏覽器載入負擔，提升使用者體驗。使用者可以透過「關鍵字搜索」景點名稱或「依捷運站一鍵篩選」查看周遭景點。


<img width="600" src="https://github.com/user-attachments/assets/2cd705ca-1547-441c-a2d6-475a15af0b74" alt="首頁截圖-景點篩選" /><br><br>

(2) 會員註冊及登入  
使用者透過任一信箱註冊後，即可完成登入。


<img width="600" src="https://github.com/user-attachments/assets/4ba3a43a-655c-4ab5-b1f3-011ddbc60084" alt="首頁截圖-會員功能" /><br><br>

(3) 景點行程預訂及付款  
使用者從首頁點選景點卡片後，即可查看景點相關資訊，並可於登入後進一步預訂景點導覽。  


<img width="600" src="https://github.com/user-attachments/assets/88d81f53-8702-4696-bff9-e539e548aeec" alt="查看景點內容與預訂" />  
<img width="600" src="https://github.com/user-attachments/assets/f8c503b1-5078-4f2c-9f0e-051c42260854" alt="付款完成確認" /><br><br>

(4) 檢視購物車與歷史訂單紀錄  
使用者登入後才能查看。  


<img width="600" src="https://github.com/user-attachments/assets/04c6f01b-1195-4ee5-aee8-73b3beaba9a6" alt="購物車與歷史訂單" /><br><br>

(5) Responsive Web Design (RWD)

<img width="800" src="https://github.com/user-attachments/assets/4a3d156a-4d38-4cc6-8869-83768d5e793d" alt="RWD示意圖" /><br><br>

## 聯絡資訊 Contact
* Name: 陳立欣
* Email: claire.hshin619@gmail.com

