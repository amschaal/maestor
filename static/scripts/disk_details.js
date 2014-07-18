function ChartsCtrl($scope,$http,$location){
	$scope.init = function(disk_id,charts){
		$scope.disk_id = disk_id;
		$scope.attrs = [];
		$http({method:'GET',params:{disk:disk_id},url:'/api/attributes/list/'}).then(function(result) {
    		$scope.attributes = result.data;
    		//console.log(result.data);
		});
		//You can initialize a page with certain charts
		var chart = getParameterByName('chart')
		if (chart){
			$scope.chart({'type':chart.split('__')[0],'name':chart.split('__')[1]});
		}
			
//		$scope.chart({'type':'smartctl','name':'Power_On_Hours'});

		//		$scope.chart({'type':'smartctl','name':'Current_Pending_Sector'});
//		$scope.chart({'type':'smartctl','name':'Offline_Uncorrectable'});
	}
	$scope.remove = function(attribute){
		$scope.attrs.splice($scope.attrs.indexOf(attribute),1);
	}
	$scope.chart = function(attribute){
		if (!attribute)
			attribute = $scope.attribute;
		attribute.clean_name = attribute.name.replace(/[^a-z0-9\s]/gi, '').replace(/[_\s]/g, '-');
		$scope.attrs.push(attribute);
		$http({url: '/api/disk/values/',
	    		method: 'GET',
	    		params: {'attribute':attribute.name,'type':attribute.type,'disk':$scope.disk_id}}).then(function(result) {
    		foo = result.data.values;
    		var data = [];
    		var datetime = result.data.fields.indexOf('datetime');
    		var value = result.data.fields.indexOf('value');
    		for (var i in foo){
    			data.push(
    					[(new Date(foo[i][datetime])).getTime(),parseFloat(foo[i][value])]
    					)
    		}
    		console.log(data);
    		$('#'+attribute.clean_name+'_chart').css('display','block').highcharts('Chart', {
    			chart: {
                    zoomType: 'x'
                },
    			title : {
    				text : attribute.name
    			},
                xAxis: {
                	events : {
    					afterSetExtremes : function(e){$scope.afterSetExtremes(e,attribute)}
    				},
    				minRange: 3600 * 1000, // one hour
                	type: 'datetime',
                    ordinal :false
                },
    			series : [{
    				name : attribute.name,
    				data : data,
    				tooltip: {
    					valueDecimals: 2
    				}
    			}]
    		});
		});
	}
	/**
	 * Load new data depending on the selected min and max
	 */
	 $scope.afterSetExtremes = function(e,attribute) {
		//var currentExtremes = this.getExtremes();
		var range = e.max - e.min;
 		var chart = $('#'+attribute.clean_name+'_chart').highcharts();
 		chart.showLoading('Loading data from server...');
		console.log('event',e,attribute);
		// If zoom reset, don't specify bounds.  Let the server do that.
		if(typeof e.userMin == 'undefined' && typeof e.userMax == 'undefined')
			var params = {'attribute':attribute.name,'type':attribute.type,'disk':$scope.disk_id};
		else
			var params = {'attribute':attribute.name,'type':attribute.type,'disk':$scope.disk_id,'start':Math.round(e.min),'end':Math.round(e.max)};
		$http({url: '/api/disk/values/',
    		method: 'GET',
    		params: params})
    		.then(function(result) {
				console.log(result);
				foo = result.data.values;
	    		var data = [];
	    		var datetime = result.data.fields.indexOf('datetime');
	    		var value = result.data.fields.indexOf('value');
	    		for (var i in foo){
	    			data.push(
	    					[(new Date(foo[i][datetime])).getTime(),parseFloat(foo[i][value])]
	    					)
	    		}
	    		chart.series[0].setData(data);
				chart.hideLoading();
		        //chart.series[0].update({type:'areasplinerange'});
			});
	}
	
	
}