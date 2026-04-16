
### Use 
- Playwright-CLI
- Playwright MCP  (all context 로 인한 token비용 cli 보다 많이 듬)


### Agent Use
#### Opencode
- playwright-cli 에서 특정 url 열어서 스크린샷 찍어줘



### Playwright Codegen
- 브라우저 스크립트 생성 => 스크립트 실행 하여 자동화 방식
	- 스크립트 생성
		- npx playwright codegen https://example.com
	- 스크립트 실행
		- npx playwright test jira_1.spec.js 
		- headed 모드로 실행 (창 보임) npx playwright test script.js --headed

### 실습
- 구글 확장 프로그램 => 밀리의서재 도서 검색 (playwright 활용 )
	- cloude code  사용
	- express server를 통해 밀리의 서재 세션 사용 
	- 로컬에서만 동작  
		- server npm start  => http://localhost:3747
