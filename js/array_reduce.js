 const orders = [
        {  livingId: 996, cash: 30500.35, tax: 0.06, isDisputed: true},
        {  livingId: 910, cash: 100, tax: 0.08, isDisputed: true },
        {  livingId: 912, cash: 4200.11, tax: 0.06 },
        {  livingId: 996, cash: 99.12, tax: 0.06, isDisputed: false },
        {  livingId: 910, cash: 0.00, tax: 0.08, isShipped: true },
        {  livingId: 996, cash: 10, tax: 0.06, isDisputed: true },
    ]

const result1 = orders.reduce((acc,val) => {
   let uniqueId = val.livingId
   let obj = acc.find(a => a.uniqueId == val.livingId)
   if(!!obj){
	  let obj = acc.find(a => a.uniqueId == val.livingId)
	  obj.numOrders++
   }else{
	  acc.push({numOrders: 1, uniqueId: uniqueId})
   }
   return acc
},[])

console.log(result1)
console.log("-------------------------------")

//---------------------------------------
// https://stackoverflow.com/questions/74334249/how-to-sum-an-array-for-each-id-and-create-new-array-in-react/

const data = [{"id": "One", "number": 100}, 
  {"id": "One", "number": 150}, 
  {"id": "One", "number": 200}, 
  {"id": "Two", "number": 50}, 
  {"id": "Two", "number": 100}, 
  {"id": "Three", "number": 10}, 
  {"id": "Three", "number": 90}]

// 自己的写法
let result2 = data.reduce((a, v) => {
  let obj = a.find(i => i.id == v.id);
  if (obj) {
      obj.number += v.number;
  } else {
      a.push({...v});
  }
  return a;
}, [])
console.log(result2);
console.log("-------------------------------")


// 更简化写法
let result3 = data.reduce((acc, {id, number}) => ({...acc, [id]: {id, number: acc[id] ? acc[id].number + number: number}}), {});
console.log(Object.values(result3));

