/* ThermoYar buying-guide research engine V1. Independent from locked V7. */
'use strict';
const areaLabels={under80:'کمتر از ۸۰ مترمربع','80-120':'۸۰ تا ۱۲۰ مترمربع','120-180':'۱۲۰ تا ۱۸۰ مترمربع',over180:'بیشتر از ۱۸۰ مترمربع'};
const floorLabels={middle:'طبقه میانی',top:'طبقه آخر',ground:'همکف یا روی پارکینگ'};
const insulationLabels={good:'خوب',average:'معمولی',poor:'ضعیف'};
function assessBoilerNeeds(input){
 const {area,bath,floor,insulation}=input||{};
 if(!Object.hasOwn(areaLabels,area)||!['1','2','3'].includes(String(bath))||!Object.hasOwn(floorLabels,floor)||!Object.hasOwn(insulationLabels,insulation)){
  return {ok:false,error:'لطفاً مشخصات محل نصب را کامل انتخاب کنید.'};
 }
 const considerations=[];
 if(floor==='top'||floor==='ground')considerations.push('شرایط سقف یا کف ممکن است اتلاف حرارت را افزایش دهد.');
 if(insulation==='poor')considerations.push('عایق‌بندی ضعیف نیازمند بررسی دقیق‌تر بار گرمایشی است.');
 if(String(bath)!=='1')considerations.push('برای چند حمام، مصرف هم‌زمان و دبی آب گرم باید بررسی شود.');
 considerations.push('مساحت دقیق، شهر و اقلیم، رادیاتورها یا گرمایش از کف باید مشخص شوند.');
 considerations.push('محل نصب، دودکش، تهویه و ایمنی گاز باید توسط متخصص بررسی شوند.');
 return {ok:true,summary:`متراژ ${areaLabels[area]}، ${bath} حمام، ${floorLabels[floor]}، عایق‌بندی ${insulationLabels[insulation]}`,
  recommendation:'با این اطلاعات نمی‌توان ظرفیت یا مدل مشخصی را با اطمینان تعیین کرد.',
  considerations,needsSpecialist:true,contactText:'برای انتخاب ظرفیت و مدل مناسب با متخصص تماس بگیرید.',
  recommendedModelIds:[],recommendedKw:null};
}
if(typeof module!=='undefined'&&module.exports)module.exports={assessBoilerNeeds};
