import Mathlib.Topology.MetricSpace.PiNat
import Mathlib.Tactic

/-! Formal results about reversible representations and the ambient prependMany metric.
NO theorem here asserts completeness of Arabic morphology or all built words.
-/
namespace RecoveryMetric

noncomputable section

-- Generic lossless patch record: removed material and edit coordinates.
structure EditRecord (α : Type) where
  start : Nat
  insertedLength : Nat
  removed : List α

def restoreEdit (out : List α) (r : EditRecord α) : List α :=
  out.take r.start ++ r.removed ++ out.drop (r.start + r.insertedLength)

theorem edit_roundtrip (left removed inserted right : List α) :
    restoreEdit (left ++ (inserted ++ right))
      ⟨left.length, inserted.length, removed⟩ = left ++ removed ++ right := by
  simp only [restoreEdit, List.take_left, List.drop_append, List.drop_left]

-- Four representation operations have distinct linguistic licensing obligations.
-- The following instantiations prove restoration, not those obligations.
inductive Sign where
  | consonant : Fin 29 → Sign
  | vowel : Fin 3 → Sign
  | sukun : Sign
  | shadda : Sign
  | tanwin : Fin 3 → Sign
  | hamza : Sign
  | hamzaSeat : Fin 5 → Sign
  deriving DecidableEq

def doubled (c : Fin 29) (v : Fin 3) : List Sign :=
  [.consonant c, .sukun, .consonant c, .vowel v]
def geminated (c : Fin 29) (v : Fin 3) : List Sign :=
  [.consonant c, .shadda, .vowel v]

theorem shadda_restore (l r : List Sign) (c : Fin 29) (v : Fin 3) :
    restoreEdit (l ++ (geminated c v ++ r))
      ⟨l.length, (geminated c v).length, doubled c v⟩ = l ++ doubled c v ++ r :=
  edit_roundtrip l (doubled c v) (geminated c v) r

-- 'noon' is a parameter: the carrier mapping is an external explicit convention.
theorem tanwin_restore (l r : List Sign) (c noon : Fin 29) (v : Fin 3) :
    restoreEdit (l ++ ([.consonant c, .tanwin v] ++ r))
      ⟨l.length, 2, [.consonant c, .vowel v, .consonant noon, .sukun]⟩ =
      l ++ [.consonant c, .vowel v, .consonant noon, .sukun] ++ r :=
  edit_roundtrip l _ _ r

theorem hamza_restore (l r : List Sign) (seat : Fin 5) :
    restoreEdit (l ++ ([.hamza] ++ r))
      ⟨l.length, 1, [.hamzaSeat seat]⟩ = l ++ [.hamzaSeat seat] ++ r :=
  edit_roundtrip l _ _ r

theorem ilal_edit_restore (l source target r : List Sign) :
    restoreEdit (l ++ (target ++ r))
      ⟨l.length, target.length, source⟩ = l ++ source ++ r :=
  edit_roundtrip l source target r

-- Without residual information, distinct seated hamzas collapse.
def eraseSeat (_ : Fin 5) : Sign := .hamza

theorem no_seat_recovery_from_hamza_alone :
    ¬ ∃ d : Sign → Fin 5, ∀ s, d (eraseSeat s) = s := by
  rintro ⟨d, h⟩
  have h0 := h (0 : Fin 5)
  have h1 := h (1 : Fin 5)
  have impossible : (0 : Fin 5) = 1 := h0.symm.trans h1
  norm_num at impossible

theorem restoration_forces_fiber_separation
    (f : α → β) (residual : α → γ) (decode : β × γ → α)
    (h : ∀ x, decode (f x, residual x) = x)
    {x y : α} (hf : f x = f y) (hr : residual x = residual y) : x = y := by
  calc
    x = decode (f x, residual x) := (h x).symm
    _ = decode (f y, residual y) := by rw [hf, hr]
    _ = y := h y

theorem compose_restoration (f : α → β) (g : β → γ)
    (df : β → α) (dg : γ → β)
    (hf : ∀ x, df (f x) = x) (hg : ∀ y, dg (g y) = y) (x : α) :
    df (dg (g (f x))) = x := by rw [hg, hf]

-- A real-valued non-discrete metric, reused from pinned mathlib.
abbrev Stream := Nat → Fin 116
local instance : TopologicalSpace (Fin 116) := ⊥
local instance : DiscreteTopology (Fin 116) := ⟨rfl⟩
noncomputable def ambientMetric : MetricSpace Stream := PiNat.metricSpace
local instance : MetricSpace Stream := ambientMetric

theorem ambient_complete : CompleteSpace Stream := PiNat.completeSpace

theorem metric_nonnegative (x y : Stream) : 0 ≤ dist x y := dist_nonneg

theorem metric_separates (x y : Stream) : dist x y = 0 ↔ x = y := dist_eq_zero

theorem metric_symmetric (x y : Stream) : dist x y = dist y x := dist_comm x y

theorem metric_ultrametric (x y z : Stream) :
    dist x z ≤ max (dist x y) (dist y z) := PiNat.dist_triangle_nonarch x y z

theorem metric_triangle (x y z : Stream) :
    dist x z ≤ dist x y + dist y z := dist_triangle x y z

def prepend (a : Fin 116) (x : Stream) : Stream
  | 0 => a
  | n + 1 => x n

def tail (x : Stream) : Stream := fun n => x (n+1)

theorem descend_ascend (a : Fin 116) (x : Stream) : tail (prepend a x) = x := rfl

theorem ascend_descend (x : Stream) : prepend (x 0) (tail x) = x := by
  funext n
  cases n <;> rfl

theorem prepend_injective (a : Fin 116) : Function.Injective (prepend a) := by
  intro x y h
  have := congrArg tail h
  exact this

theorem firstDiff_characterization {x y : Stream} (hxy : x ≠ y) (n : Nat)
    (hn : x n ≠ y n) (before : ∀ i < n, x i = y i) :
    PiNat.firstDiff x y = n := by
  apply Nat.le_antisymm
  · by_contra h
    have lt : n < PiNat.firstDiff x y := by omega
    exact hn (PiNat.apply_eq_of_lt_firstDiff lt)
  · by_contra h
    have lt : PiNat.firstDiff x y < n := by omega
    exact PiNat.apply_firstDiff_ne hxy (before _ lt)

theorem firstDiff_prepend (a : Fin 116) (x y : Stream) (hxy : x ≠ y) :
    PiNat.firstDiff (prepend a x) (prepend a y) = PiNat.firstDiff x y + 1 := by
  have hp : prepend a x ≠ prepend a y := fun h => hxy (prepend_injective a h)
  apply firstDiff_characterization hp
  · simpa [prepend] using PiNat.apply_firstDiff_ne hxy
  · intro i hi
    cases i with
    | zero => rfl
    | succ k =>
      have hk : k < PiNat.firstDiff x y := by omega
      simpa [prepend] using (PiNat.apply_eq_of_lt_firstDiff hk : x k = y k)

theorem prepend_scales_distance (a : Fin 116) (x y : Stream) :
    dist (prepend a x) (prepend a y) = (1 / 2 : ℝ) * dist x y := by
  classical
  by_cases hxy : x = y
  · subst y
    simp
  · have hp : prepend a x ≠ prepend a y := fun h => hxy (prepend_injective a h)
    rw [PiNat.dist_eq_of_ne hp, PiNat.dist_eq_of_ne hxy, firstDiff_prepend a x y hxy]
    simp [pow_succ, mul_comm]

def prependMany : List (Fin 116) → Stream → Stream
  | [], x => x
  | a :: as, x => prepend a (prependMany as x)

theorem prefix_scales_distance (p : List (Fin 116)) (x y : Stream) :
    dist (prependMany p x) (prependMany p y) = (1 / 2 : ℝ)^p.length * dist x y := by
  induction p with
  | nil => simp [prependMany]
  | cons a as ih =>
    simp only [prependMany, prepend_scales_distance, ih, List.length_cons, pow_succ]
    ring

theorem ambient_self_similarity :
    (Set.univ : Set Stream) = ⋃ a : Fin 116, Set.range (prepend a) := by
  ext x
  simp only [Set.mem_univ, Set.mem_iUnion, Set.mem_range, true_iff]
  exact ⟨x 0, tail x, ascend_descend x⟩

theorem first_cylinders_disjoint (a b : Fin 116) (hab : a ≠ b) :
    Disjoint (Set.range (prepend a)) (Set.range (prepend b)) := by
  rw [Set.disjoint_left]
  rintro x ⟨u, hu⟩ ⟨v, hv⟩
  have h : prepend a u = prepend b v := hu.trans hv.symm
  exact hab (congrFun h 0)

-- Deliberately weak initial-vowel condition, not full Arabic validity.
def InitialVowel (x : Stream) : Prop := (x 0).val % 4 ≠ 3

theorem licensed_subset_not_closed_under_all_prefixes :
    ∃ x : Stream, InitialVowel x ∧ ¬ InitialVowel (prepend 3 x) := by
  refine ⟨fun _ => (0 : Fin 116), ?_, ?_⟩
  · change (0 : Nat) % 4 ≠ 3
    decide
  · change ¬ ((3 : Nat) % 4 ≠ 3)
    decide

def Vowel (a : Fin 116) : Prop := a.val % 4 ≠ 3

def LegalStream (needsVowel : Prop) (x : Stream) : Prop :=
  (needsVowel → Vowel (x 0)) ∧
  ∀ n, ¬ Vowel (x n) → Vowel (x (n+1))

-- Exact state-dependent decomposition of the declared no-adjacent-sukun model.
-- Not a theorem about every Arabic word or its lexicon.
theorem legal_prepend_iff (needsVowel : Prop) (a : Fin 116) (x : Stream) :
    LegalStream needsVowel (prepend a x) ↔
    (needsVowel → Vowel a) ∧ LegalStream (¬ Vowel a) x := by
  constructor
  · rintro ⟨hf, hn⟩
    refine ⟨hf, ?_, ?_⟩
    · exact hn 0
    · intro n
      exact hn (n+1)
  · rintro ⟨hf, ht, hn⟩
    refine ⟨hf, ?_⟩
    intro n
    cases n with
    | zero => exact ht
    | succ n => exact hn n

theorem legal_stream_decomposition (needsVowel : Prop) (x : Stream) :
    LegalStream needsVowel x ↔
    (needsVowel → Vowel (x 0)) ∧ LegalStream (¬ Vowel (x 0)) (tail x) := by
  have h := legal_prepend_iff needsVowel (x 0) (tail x)
  rw [ascend_descend] at h
  exact h

end
end RecoveryMetric
