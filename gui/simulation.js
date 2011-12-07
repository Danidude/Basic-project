var cm = {};

cm.grids = [];

cm.log = console.log ? console.log : function(){};

cm.draw = function(){
	var grids = this.grids;
	for(var g=0,gn=grids.length;g<gn;g++)
		grids[g].draw();
};

cm.GridCell = function(args){
	$.extend(this,args);
	this._rectangle = {};
};

cm.Gradient = function(args){
	$.extend(this,args);
};

cm.Gradient.prototype = {
	color1: [34,34,34],
	color2: [255,0,0],
	getColor: function(f){
		var c1 = this.color1;
		var c2 = this.color2;
		var r = Math.round(c1[0]+(c2[0]-c1[0])*f) << 16;
		var g = Math.round(c1[1]+(c2[1]-c1[1])*f) << 8;
		var b = Math.round(c1[2]+(c2[2]-c1[2])*f);
		var rgb = (r|g|b).toString(16);
		return "#000000".substring(0,7-rgb.length) + rgb;
	}
};

cm.gradient = new cm.Gradient({});

cm.log('color',cm.gradient.getColor(0.5));

cm.GridCell.prototype = {
	x: -1,
	y: -1,
	bw: 0,
	sensor: false,
	burning: false,
	burningTime: -1,
	sensorCount: 0,
	_rectangle: null,
	draw:function(g,selected,visualization){
		var r = this._rectangle;
		
		if (visualization)
		{
			if (this.bw >= 0)
				r.fillStyle = cm.gradient.getColor(this.bw/126);
			else
				r.fillStyle='#222';
		}
		else
		{
			// TODO: Unless the state has changed,
			// the colors can be stored and reused,
			// i.e. not calculated for each draw
			if (selected)
			{
				if (this.sensorCount > 0 && this.burningTime >= 0)
					r.fillStyle = '#fc9';
				else if (this.sensorCount > 0)
					r.fillStyle = '#dd9';
				else if (this.burningTime >= 0)
					r.fillStyle='#f99';
				else
					r.fillStyle='#ccc';
			}
			else
			{
				if (this.sensorCount > 0 && this.burningTime >= 0)
					r.fillStyle = '#e60';
				else if (this.sensorCount > 0)
					r.fillStyle = '#dd0';
				else if (this.burningTime >= 0)
					r.fillStyle='#e00';
				else
					r.fillStyle='#222';
			}
		}
		
		var z = g.zoom;
		r.x = this.x*z + 0.5;
		r.y = this.y*z + 0.5;
		r.width = z;
		r.height = z;
		r.strokeWidth = 1;
		r.strokeStyle = g.borderColor;
		g.self.drawRect(r);
	},
};

cm.Grid = function(args){
	this.cells = [];
	this.sensors = [];
	$.extend(this,args);
	this.parent = $(this.parent);
	this.self = $(this.self);
	var cells = this.cells;

	var that = this;

	for(var x=0,xn=this.sizeX;x<xn;x++) 
	{
		cells[x] = [];
		for(var y=0,yn=this.sizeY;y<yn;y++)
		{
			cells[x][y] = new cm.GridCell({
				x:x,
				y:y
			});
		}
	}
	
	this.draw = function(){
		// Ensure that draw is not called too often
		clearTimeout(that._drawTimeout);
		that._drawTimeout = setTimeout(function(){that.onDraw()},200);
	};
	
	this.self.mousemove(function(ev){
		// Ensure that mouseover is not called too often
		clearTimeout(that._mouseTimeout);
		that._mouseTimeout = setTimeout(function(){
			var o = that.self.offset();
			var x = Math.floor((ev.clientX+$(window).scrollLeft()-o.left) / that.zoom);
			var y = Math.floor((ev.clientY+$(window).scrollTop()-o.top) / that.zoom);
			
			if (x==null || y==null || x < 0 || x >= that.sizeX || y < 0 || y >= that.sizeY )
			{
				that.onMouseOut(ev,that.cells[that._mouseX][that._mouseY]);
				$('#tooltip').hide();
				return;
			}
			
			if (x != that._mouseX || y != that._mouseY)
			{
				var c = that._cells;
				that.onMouseOut(ev,that.cells[that._mouseX][that._mouseY])
				that.onMouseOver(ev,that.cells[x][y]);
			}
			
			that._mouseX = x;
			that._mouseY = y;
		},10);
	});
	
	this.self.mouseout(function(ev){
		that.onMouseOut(ev,that.cells[that._mouseX][that._mouseY]);
		$('#tooltip').hide();
	});
	
	this.self.click(function(ev){
		var o = that.self.offset();
		var x = Math.floor((ev.clientX+$(window).scrollLeft()-o.left) / that.zoom);
		var y = Math.floor((ev.clientY+$(window).scrollTop()-o.top) / that.zoom);
		
		if (x==null || y==null || x < 0 || x >= that.sizeX || y < 0 || y >= that.sizeY )
			return;
		
		that.onMouseClick(ev,that.cells[x][y]);
	});
	
	cm.grids.push(this);
	
	$(document).ready(function(){
		that.self.appendTo(that.parent);
		that.draw();
	});
};

cm.Grid.prototype = {
	parent:'body',
	self:'<canvas/>',
	sizeX: 71,
	sizeY: 71,
	zoom: 8,
	visualization: false,
	backgroundColor: '#222',
	foregroundColor: '#ccc',
	borderColor: '#111',
	windMagnitude: 1,
	humidity: 50,
	chanceOfBurning: 58,
	sensitivity: 1, // how many neighboors are considered when sensing
	windDirection: 0, // radians
	nbw: null, // Neighboor weights
	cells: null,
	sensors: null,
	_time: 0,
	_mouseTimeout: null,
	_mouseX: 0,
	_mouseY: 0,
	draw: null,
	_drawTimeout: null,
	_calculateWeights:function(sensitivity){
		// neighboor contribution weight array
		// contribution for neighboor (x,y) is stored at [x][y]
		// weights range from 0 to 1
		this.nbw = this.nbw ? this.nbw : [];
		var nbw = this.nbw[sensitivity] = this.nbw[sensitivity] ? this.nbw[sensitivity] : [];
		
		// vector 'v' from center to neighboor (x,y) when iterating
		var vx,vy;
		
		// wind vector 'w'
		var wd = parseInt($('#windDir').val()) * Math.PI/180;
		var wm = parseInt($('#windMag').val());

		wm = wm == 0 ? 1 : wm;
		
		var wx = wm * Math.cos(wd);
		var wy = wm * Math.sin(wd);
		
		// given any integer number, (1+number*2) is always odd
		// this is a suitable property for the neighboor hood size/length
		// since it always have a definite center
		var nbhl = 1+(sensitivity<<1);
		
		for(var x=0;x<nbhl;x++)
		{
			nbw[x] = [];
			for(var y=0;y<nbhl;y++)
			{
				// calculate vector v from center to neighboor
				vx = x-sensitivity;
				vy = sensitivity-y;

				// calculate cosine value of angle 'a' between wind 'w' and vector 'v'
				// cos(a) = v*w / |v|*|w|
				var a = vx*wx+vy*wy;
				if (Math.abs(a)<=0.0001)
				{
					nbw[x][y] = 0;
					continue;
				}
				
				var b = Math.sqrt(vx*vx+vy*vy);
				if (Math.abs(b)<=0.0001)
				{
					nbw[x][y] = 0;
					continue;
				}
				
				var c = Math.sqrt(wx*wx+wy*wy);
				if (Math.abs(c)<=0.0001)
				{
					nbw[x][y] = 0;
					continue;
				}
				
				var d = b*c;
				if (Math.abs(d)<=0.0001)
				{
					nbw[x][y] = 0;
					continue;
				}
				
				var weight = a / d;
				
				// wind may only point to center when cosine value is in range [-1,0]
				// '-1' gives the best effect and 1 gives negative effect (opposite direction).
				// therefore, set weight to 0 (no contribution) for any positive value
				if (weight>0)
				{
					nbw[x][y] = 0;
					continue; 
				}
				
				// to simplify, the absolute value will have a range [0,1] where 1 is the best
				// now we can multiply it directly with any neighboor magnitude to determine
				// the contribution from this neighboor on the center
				weight = Math.abs(weight);
				
				weight = Math.abs(vx-vy)<=1.5 ? weight/2 : weight;
				
				nbw[x][y] = weight;
			}
		}
	},
	_next: function(){
		this._calculateWeights(1);
		this._calculateWeights(2);

		//	When iterating over the grid, neighboors have fixed indicies
		//	where (1,1) is the cell to evaluate (not a neighboor)
		//
		//		(0,0) (1,0) (2,0)
		//		(0,1) (1,1) (2,1)	----->  x
		//		(0,2) (1,2) (2,2)
		//	
		//				|
		//				|
		//				V
		//				y
		//
		//	Given a constant wind direction and magnitude over the area at a given time,
		//	the weighted contribution from each neighboor is constant. We can pre-calculate
		//	these weights and re-use them for each iteration.
		
		
		//	The cells to iterate
		var cells = this.cells;
		
		var sensitivity = this.sensitivity;
		
		
		var humidity = 5-Math.round(parseInt($('#himidity').val())/10);
		
		var time = ++this._time; // time now

		// cell 2d range from (x,y) to (xn,yn) exclusive 
		var x=0,xn=this.sizeX;
		var y=0,yn=this.sizeY;
		
		// current cell to evaluate
		var cell = null;
		var wm = parseInt($('#windMag').val());

		for(x=0;x<xn;x++)
		{
			for(y=0;y<yn;y++)
			{
				cell = cells[x][y];
				if (cell.burningTime < 0 && cell.burningTime != time)
				{
					var bw = this.evaluateCell(cell,1);
					cell.bw = bw;

					if (bw > 0)
					{
						// bw >= bwn spontaneous combustion
						if ( bw >= Math.floor(Math.random()*10) )
						{
							cell.burningTime = time;
						}
					}
				}
			}
		}
		
		this.walkSensors();
		this.evaluate();
	},
	evaluateCell: function(cell,sensitivity,sensor){
		var nbw = this.nbw;
		var cells = this.cells;
		
		// ending index of neighboorhood in cells (inclusive)
		var nxl = cell.x+sensitivity;
		var nyl = cell.y+sensitivity;
		
		// burning weight
		var bw = 0;
		var hasBurningNeighbor = false;
		
		var dx,dy;
		var sqrt3 = Math.sqrt(3);
		
		for(var nx=cell.x-sensitivity;nx<=nxl;nx++)
		{
			for(var ny=cell.y-sensitivity;ny<=nyl;ny++)
			{
				if (cells[nx] && cells[nx][ny])
				{
					if (nx==cell.x && ny==cell.y)
					{
						// not a neighboor, i.e. cant evaluate itself
						continue;
					}
					else
					{
						var nc = cells[nx][ny];
						
						if ( nc.burningTime >=0 )
						{
							if(sensor||nc.burningTime != this._time)
							{
								bw+=this.nbw[sensitivity][nxl-nx][nyl-ny];
							}
							dx = (nx-cell.x);
							dy = (ny-cell.y);
							hasBurningNeighbor = Math.sqrt(dx*dx+dy*dy)/sqrt3<sensitivity;
						}
					}
				}
			}
		}
		
		
		return Math.ceil(bw) == 0 ? (hasBurningNeighbor && sensor ? 1 : 0) : Math.ceil(bw);
	},
	addSensor:function(x,y){
		var c = this.cells[x][y];
		if (c)
		{
			c.sensorCount++;
			this.sensors.push(c);
		}
	},
	setDataFrom1D:function(data)
	{
		var i = 0;
		var cc,c = null;
		
		for(var x=0,nx=this.sizeX;x<nx;x++)
		{
			for(var y=0,ny=this.sizeY;y<ny;y++)
			{
				cc = parseInt(data.charCodeAt(i));
				c = this.cells[x][y];

				if (cc == 0)
				{
					c.bw = 0;
					c.burningTime = -1;
				}
				else
				{
					c.bw = cc;
					c.burningTime = this._time;
				}
				
				i++;
			}
		}
		
		this.draw();
	},
	onMouseClick:function(ev,cell){
		cell.burningTime = this._time;
		cell.bw = 0;
		cell.draw(this,false);
	},
	onMouseOver:function(ev,cell){
		cell.draw(this,true);
		var o = this.self.offset();
		var z = this.zoom;
		$('#tooltip').text('['+cell.x+','+cell.y+","+cell.bw+']')
		.css('left',cell.x*z+o.left+(z<<1))
		.css('top',cell.y*z+o.top+(z<<1)).show();
	},
	onMouseOut:function(ev,cell){
		cell.draw(this,false,this.visualization);
	},
	onDraw:function(){		
		var p = this.parent;
		var s = this.self;
		s.attr('width',(this.sizeX*this.zoom+1)+"px");
		s.attr('height',(this.sizeY*this.zoom+1)+"px");
		s.loadCanvas();
		
		var c = this.cells;
		
		for(var x=0,nx=this.sizeX;x<nx;x++)
			for(var y=0,ny=this.sizeY;y<ny;y++)
				c[x][y].draw(this,false,this.visualization);
	},
	onGaussianSuccess:function(data){
		cm.log(data);
	},
	walkSensors:function(){
		var sensors = this.sensors;
		for(var s=0,sn=sensors.length;s<sn;s++)
		{
			if (sensors[s].burningTime>=0)
			{
				var x = Math.round(Math.random()*(this.sizeX-1));
				var y = Math.round(Math.random()*(this.sizeY-1));
				
				if (this.cells[x] && this.cells[x][y] && this.cells[x][y].burningTime < 0)
				{
					sensors[s].sensorCount--;
					sensors[s] = this.cells[x][y];
					sensors[s].sensorCount++;
				}
				else
				{
					sensors[s].sensorCount--;
				}
			}
			
			if (Math.random()>0.4)
				continue;
			
			x0 = sensors[s].x;
			y0 = sensors[s].y;
			
			//	generate direction
			//
			//		1 2 3
			//		4   5
			//		6 7 8
			
			switch(1+Math.round(Math.random()*7))
			{
				case 1:
				{
					x1 = x0-1;
					y1 = y0-1;
					break;
				}
				case 2:
				{
					x1 = x0;
					y1 = y0-1;
					break;
				}
				case 3:
				{
					x1 = x0+1;
					y1 = y0-1;
					break;
				}
				case 4:
				{
					x1 = x0-1;
					y1 = y0;
					break;
				}
				case 5:
				{
					x1 = x0+1;
					y1 = y0;
					break;
				}
				case 6:
				{
					x1 = x0-1;
					y1 = y0+1;
					break;
				}
				case 7:
				{
					x1 = x0;
					y1 = y0+1;
					break;
				}
				case 8:
				{
					x1 = x0+1;
					y1 = y0+1;
					break;
				}
			}
			
			if (this.cells[x1] && this.cells[x1][y1] && this.cells[x1][y1].burningTime < 0)
			{
				sensors[s].sensorCount--;
				sensors[s] = this.cells[x1][y1];
				sensors[s].sensorCount++;
			}
		}
	},
	evaluate:function(){
		var cells = this.cells;
		var sensors = this.sensors;
		var readings = [];

		for(var x=0,nx=this.sizeX;x<nx;x++)
			for(var y=0,ny=this.sizeY;y<ny;y++)
			{
				cells[x][y].bw = this.evaluateCell(cells[x][y],2,true);

				if (cells[x][y].sensorCount > 0)
					readings.push(String.fromCharCode(cells[x][y].bw));
				else
					readings.push(String.fromCharCode(127));
			}

		var that = this;
		$.ajax({
			url:'http://localhost:8000/simulate/fire',
			type: 'post',
			dataType: 'text',
			data: {
				time: that._time,
				sizeX: that.sizeX,
				sizeY: that.sizeY,
				windDirection: that.windDirection,
				cells: Base64.encode(readings.join(''))
			},
			success:function(data){
				that.onGaussianSuccess(Base64.decode(data));
			},
			failure:function(){
				cm.log("ajax failure");
			}
		});
	}
};

$.jCanvas({
	fromCenter: false,
	strokeWidth: 0,
	strokeStyle: "#111",
	strokeJoin: "miter",
	strokeCap: "square"
});

$(window).resize(function(){
	cm.draw();
});

$(document).ready(function(){
	
});