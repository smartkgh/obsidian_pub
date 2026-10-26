var m=Object.defineProperty;var y=Object.getOwnPropertyDescriptor;var b=Object.getOwnPropertyNames;var v=Object.prototype.hasOwnProperty;var D=(o,n)=>{for(var t in n)m(o,t,{get:n[t],enumerable:!0})},P=(o,n,t,s)=>{if(n&&typeof n=="object"||typeof n=="function")for(let a of b(n))!v.call(o,a)&&a!==t&&m(o,a,{get:()=>n[a],enumerable:!(s=y(n,a))||s.enumerable});return o};var $=o=>P(m({},"__esModule",{value:!0}),o);var N={};D(N,{default:()=>f});module.exports=$(N);var e=require("obsidian"),k={folder:"QT",dateFormat:"YYYY-MM-DD",defaultBook:""};function E(o,n,t,s,a){return`---
date: ${o}
passage: "${n}"
book: "${t}"
chapter: "${s}"
verse: "${a}"
tags:
  - QT
  - \uBB35\uC0C1
---

# \u{1F4D6} ${n}

## \u{1F4DD} \uBCF8\uBB38 (Scripture)

> *\uC5EC\uAE30\uC5D0 \uC131\uACBD \uAD6C\uC808\uC744 \uC785\uB825\uD558\uC138\uC694*

---

## \u{1F50D} \uAD00\uCC30 (Observation)

*\uBCF8\uBB38\uC5D0\uC11C \uBB34\uC5C7\uC744 \uBC1C\uACAC\uD588\uB098\uC694? \uC0AC\uC2E4(fact)\uB9CC \uAE30\uB85D\uD569\uB2C8\uB2E4.*

- 

---

## \u{1F4A1} \uC801\uC6A9 (Application)

*\uC624\uB298 \uB098\uC758 \uC0B6\uC5D0 \uC5B4\uB5BB\uAC8C \uC801\uC6A9\uD560 \uC218 \uC788\uB098\uC694?*

- 

---

## \u{1F64F} \uAE30\uB3C4 (Prayer)

*\uB9D0\uC500\uC744 \uBB35\uC0C1\uD55C \uD6C4 \uD558\uB098\uB2D8\uAED8 \uB4DC\uB9AC\uB294 \uAE30\uB3C4*

> 

---

## \u{1F5DD}\uFE0F \uD575\uC2EC \uB2E8\uC5B4/\uAD6C\uC808 (Key Word)

> 

---

*${o} \xB7 QT*
`}var u=class extends e.Modal{constructor(t,s){super(t);this.plugin=s}onOpen(){let{contentEl:t}=this;t.empty(),t.addClass("qt-modal"),t.createDiv("qt-modal-header").createEl("h2",{text:"\u271D\uFE0F QT \uB178\uD2B8 \uC0DD\uC131"});let a=(0,e.moment)().format("YYYY-MM-DD"),h=a,d=this.plugin.settings.defaultBook,l="",c="",g=t.createDiv("qt-modal-form");new e.Setting(g).setName("\uB0A0\uC9DC").setDesc("QT \uB0A0\uC9DC\uB97C \uC120\uD0DD\uD558\uC138\uC694").addText(i=>{i.inputEl.type="date",i.setValue(a),i.onChange(r=>h=r)}),new e.Setting(g).setName("\uC131\uACBD \uCC45").setDesc("\uC608: \uC694\uD55C\uBCF5\uC74C, \uC2DC\uD3B8, \uB85C\uB9C8\uC11C").addText(i=>{i.setPlaceholder("\uC694\uD55C\uBCF5\uC74C").setValue(d),i.onChange(r=>d=r)}),new e.Setting(g).setName("\uC7A5 (Chapter)").addText(i=>{i.setPlaceholder("3").setValue(l),i.onChange(r=>l=r)}),new e.Setting(g).setName("\uC808 (Verse)").setDesc("\uC608: 1-16, 1\uC808, \uC804\uCCB4").addText(i=>{i.setPlaceholder("16").setValue(c),i.onChange(r=>c=r)});let p=t.createDiv("qt-modal-btns");p.createEl("button",{text:"\uCDE8\uC18C",cls:"qt-btn-cancel"}).addEventListener("click",()=>this.close()),p.createEl("button",{text:"\uB178\uD2B8 \uC0DD\uC131",cls:"qt-btn-create"}).addEventListener("click",async()=>{if(!d||!l){new e.Notice("\u26A0\uFE0F \uC131\uACBD \uCC45\uACFC \uC7A5\uC744 \uC785\uB825\uD574 \uC8FC\uC138\uC694.");return}let i=c?`${d} ${l}:${c}`:`${d} ${l}\uC7A5`;await this.plugin.createQTNote(h,i,d,l,c),this.close()})}onClose(){this.contentEl.empty()}},f=class extends e.Plugin{async onload(){await this.loadSettings(),this.addRibbonIcon("book-open","QT \uB178\uD2B8 \uC0DD\uC131",()=>{new u(this.app,this).open()}),this.addCommand({id:"open-qt-modal",name:"QT \uB178\uD2B8 \uC0DD\uC131 (\uBAA8\uB2EC)",callback:()=>{new u(this.app,this).open()}}),this.addCommand({id:"create-qt-today",name:"\uC624\uB298 QT \uB178\uD2B8 \uBE60\uB978 \uC0DD\uC131",callback:async()=>{let t=(0,e.moment)().format("YYYY-MM-DD");await this.createQTNote(t,"","","","")}}),this.addSettingTab(new T(this.app,this))}async createQTNote(t,s,a,h,d){let l=this.settings.folder,c=`${t}-QT.md`,g=l?`${l}/${c}`:c;l&&(this.app.vault.getAbstractFileByPath(l)||await this.app.vault.createFolder(l));let p=this.app.vault.getAbstractFileByPath(g);if(p){await this.app.workspace.getLeaf(!1).openFile(p),new e.Notice(`\u{1F4D6} \uAE30\uC874 QT \uB178\uD2B8\uB97C \uC5F4\uC5C8\uC2B5\uB2C8\uB2E4: ${c}`);return}let w=E(t,s,a,h,d),Q=await this.app.vault.create(g,w);await this.app.workspace.getLeaf(!1).openFile(Q),new e.Notice(`\u2705 QT \uB178\uD2B8\uAC00 \uC0DD\uC131\uB418\uC5C8\uC2B5\uB2C8\uB2E4: ${c}`)}async loadSettings(){this.settings=Object.assign({},k,await this.loadData())}async saveSettings(){await this.saveData(this.settings)}},T=class extends e.PluginSettingTab{constructor(t,s){super(t,s);this.plugin=s}display(){let{containerEl:t}=this;t.empty(),t.createEl("h2",{text:"QT Note Creator \uC124\uC815"}),new e.Setting(t).setName("\uC800\uC7A5 \uD3F4\uB354").setDesc("QT \uB178\uD2B8\uAC00 \uC800\uC7A5\uB420 \uD3F4\uB354 \uACBD\uB85C (\uBE44\uC6CC\uB450\uBA74 vault \uB8E8\uD2B8)").addText(s=>s.setPlaceholder("QT").setValue(this.plugin.settings.folder).onChange(async a=>{this.plugin.settings.folder=a.trim(),await this.plugin.saveSettings()})),new e.Setting(t).setName("\uAE30\uBCF8 \uC131\uACBD \uCC45").setDesc("\uBAA8\uB2EC \uC5F4 \uB54C \uBBF8\uB9AC \uCC44\uC6CC\uC9C8 \uC131\uACBD \uCC45 \uC774\uB984").addText(s=>s.setPlaceholder("\uC694\uD55C\uBCF5\uC74C").setValue(this.plugin.settings.defaultBook).onChange(async a=>{this.plugin.settings.defaultBook=a.trim(),await this.plugin.saveSettings()}))}};
