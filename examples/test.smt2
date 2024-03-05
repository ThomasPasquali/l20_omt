;e^(x)-3=sin(y)
;cos(y) = cos(x) * sin(x^(3)-0.2)
; x-y >= cos(0.2)
; x+y <= sin(0.2)

(set-logic QF_NRA)
(declare-fun x () Real)
;(declare-fun y () Real)
;(declare-fun z () Real)
;(declare-fun pi () Real)
;(declare-fun exp (Real) Real)
;(assert (= z 0.2))
;(assert (<= z pi))
;(assert (>= z 0.1))
;(assert (>= x 2))
;(assert (<= (* x (* x 2) 4) (cos z)))
;(assert (>= (+ x y) (sin z)))
;(assert (or (= 0 (cos y)) (= (sin y) (+ 0.0000001 (exp x))) (= (sin y) (exp x))))
;(assert (or (= 0 (sin y)) (= (cos y) (sin (- (^ x 3) z)))))

; From slides
(assert (<= 0 (sin x)))
(assert (<= 0 (- (/ (* x x) 2) 1)))
(assert (<= 0 (- (* 3 x) 2)))
(minimize (+ (* (* x x) 2) (* x 3) 1))
(check-sat)
(exit)



    magnitude = 5e-2
    magnitude_limit = 10

	\begin{alignat*}{2}
	& \qquad \qquad \qquad \qquad \qquad \phi := C_1 \land C_2 \land C_3 \land C_4  \\
		& C_1 \ \equiv \ y<0 \ \lor \ sin(y) = e^x -3 
		&& C_3 \ \equiv \ x-y \geq cos(z) \\ 
		& C_2 \ \equiv \  y>0 \ \lor \  cos(y) = sin(x^3-z) 
		&& C_4 \ \equiv \ x+y \leq sin(0.2) 
		\end{alignat*}