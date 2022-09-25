 const orders = [
        {  livingId: 996, cash: 30500.35, tax: 0.06, isDisputed: true},
        {  livingId: 910, cash: 100, tax: 0.08, isDisputed: true },
        {  livingId: 912, cash: 4200.11, tax: 0.06 },
        {  livingId: 996, cash: 99.12, tax: 0.06, isDisputed: false },
        {  livingId: 910, cash: 0.00, tax: 0.08, isShipped: true },
        {  livingId: 996, cash: 10, tax: 0.06, isDisputed: true },
    ]

    const result = orders.reduce((acc,val) => {
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

    console.log(result)