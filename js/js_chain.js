// https://stackoverflow.com/questions/74354810/getting-total-from-2-objects-pushing-to-new-array
const data = [
 { 

    color: 'red',
     order_date: '2022-11-01',
     size: '9',
     orders: 4

}, 
{ 

    color: 'red',
     order_date: '2022-11-01',
     size: '11',
     orders: 8

}, 
{ 

    color: 'yellow',
     order_date: '2022-11-04',
     size: '9',
     orders: 1

}, 

{ 

    color: 'yellow',
     order_date: '2022-11-04',
     size: '11',
     orders: 4

}
]


let result = Object.values(data.reduce((a,{order_date,size,orders}) =>
({...a, [order_date]: 
	{'orderDate':order_date,
	'sizeNineTotal':(size == 9 ? orders : 0) + (a[order_date]?.sizeNineTotal??0),
	'sizeElevenTotal':(size == 11 ? orders : 0) + (a[order_date]?.sizeElevenTotal??0),
	'totalOrders': orders + (a[order_date]?.totalOrders??0)}
}), {}))
console.log(result)