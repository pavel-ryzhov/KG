package main

import (
	"image/color"

	"fyne.io/fyne/v2"
	"fyne.io/fyne/v2/canvas"
	"fyne.io/fyne/v2/container"
	"fyne.io/fyne/v2/widget"
)

type areaPicker struct {
	widget.BaseWidget
	Hue      float64
	S, L     float64
	OnChange func(s, l float64)
}

func newAreaPicker(onChange func(s, l float64)) *areaPicker {
	p := &areaPicker{OnChange: onChange}
	p.ExtendBaseWidget(p)
	return p
}

func (p *areaPicker) update(pos fyne.Position) {
	w, h := p.Size().Width, p.Size().Height
	if w == 0 || h == 0 {
		return
	}
	if pos.X < 0 {
		pos.X = 0
	}
	if pos.X > w {
		pos.X = w
	}
	if pos.Y < 0 {
		pos.Y = 0
	}
	if pos.Y > h {
		pos.Y = h
	}

	p.S = float64(pos.X / w * 100.0)
	p.L = float64(1.0-pos.Y/h) * 100.0
	p.Refresh()
	if p.OnChange != nil {
		p.OnChange(p.S, p.L)
	}
}
func (p *areaPicker) Tapped(e *fyne.PointEvent) { p.update(e.Position) }
func (p *areaPicker) Dragged(e *fyne.DragEvent) { p.update(e.Position) }
func (p *areaPicker) DragEnd()                  {}

type areaRenderer struct {
	picker *areaPicker
	raster *canvas.Raster
	marker *canvas.Circle
}

func (p *areaPicker) CreateRenderer() fyne.WidgetRenderer {
	raster := canvas.NewRasterWithPixels(func(x, y, w, h int) color.Color {
		s := float64(x) / float64(w) * 100.0
		l := (1.0 - float64(y)/float64(h)) * 100.0
		rgb := HLS{H: uint16(p.Hue), L: uint8(l), S: uint8(s)}.ToRGB()
		return color.RGBA{R: rgb.R, G: rgb.G, B: rgb.B, A: 255}
	})
	marker := canvas.NewCircle(color.Transparent)
	marker.StrokeColor = color.White
	marker.StrokeWidth = 2
	return &areaRenderer{picker: p, raster: raster, marker: marker}
}
func (r *areaRenderer) Destroy() {}
func (r *areaRenderer) Objects() []fyne.CanvasObject {
	return []fyne.CanvasObject{r.raster, r.marker}
}
func (r *areaRenderer) Refresh() {
	r.Layout(r.picker.Size())
	r.raster.Refresh()
	r.marker.Refresh()
}
func (r *areaRenderer) Layout(size fyne.Size) {
	r.raster.Resize(size)
	ms := float32(12)
	r.marker.Resize(fyne.NewSize(ms, ms))
	x := float32(r.picker.S/100.0) * size.Width
	y := float32(1.0-r.picker.L/100.0) * size.Height
	r.marker.Move(fyne.NewPos(x-ms/2, y-ms/2))
}
func (r *areaRenderer) MinSize() fyne.Size { return fyne.NewSize(150, 150) }

type huePicker struct {
	widget.BaseWidget
	H        float64
	OnChange func(h float64)
}

func newHuePicker(onChange func(h float64)) *huePicker {
	p := &huePicker{OnChange: onChange}
	p.ExtendBaseWidget(p)
	return p
}

func (p *huePicker) update(pos fyne.Position) {
	w := p.Size().Width
	if w == 0 {
		return
	}
	if pos.X < 0 {
		pos.X = 0
	}
	if pos.X > w {
		pos.X = w
	}

	p.H = float64(pos.X / w * 360.0)
	if p.H > 360 {
		p.H = 360
	}
	if p.H < 0 {
		p.H = 0
	}
	p.Refresh()
	if p.OnChange != nil {
		p.OnChange(p.H)
	}
}
func (p *huePicker) Tapped(e *fyne.PointEvent) { p.update(e.Position) }
func (p *huePicker) Dragged(e *fyne.DragEvent) { p.update(e.Position) }
func (p *huePicker) DragEnd()                  {}

type hueRenderer struct {
	picker *huePicker
	raster *canvas.Raster
	marker *canvas.Rectangle
}

func (p *huePicker) CreateRenderer() fyne.WidgetRenderer {
	raster := canvas.NewRasterWithPixels(func(x, y, w, h int) color.Color {
		hue := float64(x) / float64(w) * 360.0
		rgb := HLS{H: uint16(hue), L: 50, S: 100}.ToRGB()
		return color.RGBA{R: rgb.R, G: rgb.G, B: rgb.B, A: 255}
	})
	marker := canvas.NewRectangle(color.White)
	marker.StrokeColor = color.Black
	marker.StrokeWidth = 1
	return &hueRenderer{picker: p, raster: raster, marker: marker}
}
func (r *hueRenderer) Destroy() {}
func (r *hueRenderer) Objects() []fyne.CanvasObject {
	return []fyne.CanvasObject{r.raster, r.marker}
}
func (r *hueRenderer) Refresh() {
	r.Layout(r.picker.Size())
	r.raster.Refresh()
	r.marker.Refresh()
}
func (r *hueRenderer) Layout(size fyne.Size) {
	r.raster.Resize(size)
	mw := float32(6)
	r.marker.Resize(fyne.NewSize(mw, size.Height+4))
	x := float32(r.picker.H/360.0) * size.Width
	r.marker.Move(fyne.NewPos(x-mw/2, -2))
}
func (r *hueRenderer) MinSize() fyne.Size { return fyne.NewSize(150, 20) }

type CustomPalette struct {
	Area      *areaPicker
	Hue       *huePicker
	Container *fyne.Container
}

func NewCustomPalette(onSelected func(hls HLS)) *CustomPalette {
	p := &CustomPalette{}

	p.Area = newAreaPicker(func(s, l float64) {
		onSelected(HLS{H: uint16(p.Hue.H), L: uint8(l), S: uint8(s)})
	})

	p.Hue = newHuePicker(func(h float64) {
		p.Area.Hue = h
		p.Area.Refresh()
		onSelected(HLS{H: uint16(h), L: uint8(p.Area.L), S: uint8(p.Area.S)})
	})

	p.Container = container.NewBorder(nil, container.NewPadded(p.Hue), nil, nil, p.Area)
	return p
}

func (p *CustomPalette) SetColor(hls HLS) {
	p.Hue.H = float64(hls.H)
	p.Area.Hue = float64(hls.H)
	p.Area.S = float64(hls.S)
	p.Area.L = float64(hls.L)

	p.Hue.Refresh()
	p.Area.Refresh()
}
