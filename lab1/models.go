package main

import (
	"fmt"
	"math"
	"strconv"
	"strings"
)

type RGB struct {
	R, G, B uint8
}

type CMYK struct {
	C, M, Y, K uint8
}

type HLS struct {
	H    uint16
	L, S uint8
}

func clampUint[T uint | uint8 | uint16 | uint32 | uint64](val float64, min, max T) T {
	rounded := math.Round(val)
	if rounded < float64(min) {
		return min
	}
	if rounded > float64(max) {
		return max
	}
	return T(rounded)
}

func (rgb RGB) ToCMYK() CMYK {
	r := float64(rgb.R) / 255.0
	g := float64(rgb.G) / 255.0
	b := float64(rgb.B) / 255.0
	k := 1.0 - max(r, g, b)
	if k >= 1.0 {
		return CMYK{C: 0, M: 0, Y: 0, K: 100}
	}
	c := (1.0 - r - k) / (1.0 - k)
	m := (1.0 - g - k) / (1.0 - k)
	y := (1.0 - b - k) / (1.0 - k)
	return CMYK{
		C: clampUint[uint8](c*100.0, 0, 100),
		M: clampUint[uint8](m*100.0, 0, 100),
		Y: clampUint[uint8](y*100.0, 0, 100),
		K: clampUint[uint8](k*100.0, 0, 100),
	}
}

func (rgb RGB) ToHLS() HLS {
	r := float64(rgb.R) / 255.0
	g := float64(rgb.G) / 255.0
	b := float64(rgb.B) / 255.0
	mx := max(r, g, b)
	mn := min(r, g, b)
	delta := mx - mn
	var h, l, s float64
	l = (mx + mn) / 2.0
	if delta == 0 {
		h = 0
		s = 0
	} else {
		if l <= 0.5 {
			s = delta / (mx + mn)
		} else {
			s = delta / (2.0 - mx - mn)
		}
		switch mx {
		case r:
			h = (g - b) / delta
			if g < b {
				h += 6.0
			}
		case g:
			h = ((b - r) / delta) + 2.0
		case b:
			h = ((r - g) / delta) + 4.0
		}
		h *= 60.0
	}
	roundedH := uint16(math.Round(h))
	if roundedH >= 360 {
		roundedH = 0
	}
	return HLS{
		H: roundedH,
		L: clampUint[uint8](l*100.0, 0, 100),
		S: clampUint[uint8](s*100.0, 0, 100),
	}
}

func (cmyk CMYK) ToRGB() RGB {
	c := float64(cmyk.C) / 100.0
	m := float64(cmyk.M) / 100.0
	y := float64(cmyk.Y) / 100.0
	k := float64(cmyk.K) / 100.0
	r := 255.0 * (1.0 - c) * (1.0 - k)
	g := 255.0 * (1.0 - m) * (1.0 - k)
	b := 255.0 * (1.0 - y) * (1.0 - k)
	return RGB{
		R: clampUint[uint8](r, 0, 255),
		G: clampUint[uint8](g, 0, 255),
		B: clampUint[uint8](b, 0, 255),
	}
}

func (hls HLS) ToRGB() RGB {
	h := float64(hls.H)
	l := float64(hls.L) / 100.0
	s := float64(hls.S) / 100.0
	if s == 0 {
		val := clampUint[uint8](l*255.0, 0, 255)
		return RGB{R: val, G: val, B: val}
	}
	c := (1.0 - math.Abs(2.0*l-1.0)) * s
	x := c * (1.0 - math.Abs(math.Mod(h/60.0, 2.0)-1.0))
	m := l - c/2.0
	var r1, g1, b1 float64
	switch {
	case h >= 0 && h < 60:
		r1, g1, b1 = c, x, 0
	case h >= 60 && h < 120:
		r1, g1, b1 = x, c, 0
	case h >= 120 && h < 180:
		r1, g1, b1 = 0, c, x
	case h >= 180 && h < 240:
		r1, g1, b1 = 0, x, c
	case h >= 240 && h < 300:
		r1, g1, b1 = x, 0, c
	default:
		r1, g1, b1 = c, 0, x
	}
	return RGB{
		R: clampUint[uint8]((r1+m)*255.0, 0, 255),
		G: clampUint[uint8]((g1+m)*255.0, 0, 255),
		B: clampUint[uint8]((b1+m)*255.0, 0, 255),
	}
}

func (rgb RGB) ToHEX() string {
	return fmt.Sprintf("#%02X%02X%02X", rgb.R, rgb.G, rgb.B)
}

func HEXToRGB(hexStr string) (RGB, error) {
	hexStr = strings.TrimPrefix(hexStr, "#")
	if len(hexStr) != 6 {
		return RGB{}, fmt.Errorf("неверный формат HEX")
	}
	val, err := strconv.ParseUint(hexStr, 16, 32)
	if err != nil {
		return RGB{}, err
	}
	return RGB{
		R: uint8((val >> 16) & 0xFF),
		G: uint8((val >> 8) & 0xFF),
		B: uint8(val & 0xFF),
	}, nil
}
