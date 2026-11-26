# Root independent mathematical review, edition 23

This is a working review, not a claim that final files or publication are complete.

## Source observations

French physical 90–94 contains the complete first essay §15. French 95 begins the separate short text / second essay §16, already represented by inherited `text/v1_2.tex` as V.1 (old IV.16); next work must recollate it, not add a second duplicate. English §15 runs title at59 to end61, next §16 at62.

The French p92 insertion reads `ici et plus tard`; the English labels it a long illegible segment. French p93 uses the nonempty sign in its primitive axiom and f(Z) in its image-dimension condition. The English reverses these. French p94 explicitly contains the inference concerning variants of (2.12) through (2.18), omitted or replaced in the English. The French p93 last bad-locus term is the total incidence projection to P, without a fiber subscript; it must be differentiated from the quasi-finite incidence map into P times G.

## Dimension check

For the standard line incidence over P², N=2,m=1. Let X=P³ disjoint-union L, with the P³ component mapping constantly to a rational point and L=P¹ mapping as a line. The maximum source dimension is3 and maximum image dimension is1. A generic line avoids the constant image point and meets L in one point; the generic section has dimension0, not3−1. The correct formula is the maximum of dim(Z_i)−m over irreducible components with dim closure(f(Z_i)) at least m. If none survive it is empty.

To derive nonemptiness for larger-dimensional images from the m-dimensional closed-set axiom, image constructibility cannot be omitted: choose a dense open U in the image closure actually contained in the image, then an m-dimensional irreducible closed W meeting U. The smooth surjective geometrically irreducible pullback over W is irreducible; its nonempty restriction over U remains dominant over G. Universal surjectivity of the restricted source map then gives generic nonemptiness. Explicit finite-type scope and m>=0 are necessary to this proof.

## Nonreduced base counterexample

Take an algebraically closed field k, P=A¹, G=Spec k[t,epsilon]/epsilon², N=m=1, and Pcal=Spec k[t]. Its map to P is x=t (an isomorphism), and its map into P times G is a closed immersion. For every x and n=1 tangent subspace, the geometric fiber is either empty or a reduced point, with zero tangent space transverse to the whole tangent of P. Thus all E(x,V) are empty. With X=P and f=id, the map Xcal=A¹ to G is not flat anywhere, hence not smooth anywhere. Its entire one-dimensional source is the original relative bad locus, contradicting dim E <=N−1=0. Its generic fiber is still Spec k(t), which is smooth; this refutes the original proof step, not the generic-fiber conclusion.

A valid proof repair: Pcal and Xcal are smooth over k, hence reduced, so their maps factor through G_red. Apply generic flatness to both maps and choose a common nonempty open U of the integral G_red. At points over U, fiberwise smoothness is equivalent to relative smoothness. Replace the erroneous ramification term for Pcal→P by the quasi-finite incidence map Pcal→P×G (equivalently its fiber map). The union of the two nonsmooth loci and this ramification locus is closed over U. At every closed x it maps quasi-finitely into the given bad-parameter set for the injective tangent image of df; transversality and the Jacobian criterion justify that containment. Then dim E<=n+(N−n−1)=N−1. Its generic fiber is empty. This is expressly a translator proof repair; G is not silently assumed smooth or reduced in the original statement.

An independent example for the wrongly selected ramification map is ordinary P² line incidence: the projection to P is smooth of relative dimension1, hence ramified everywhere, whereas the incidence immersion into P×dual(P) is unramified. With X=P all smoothness/transversality conditions are good, yet the original third bad term would include the entire3-dimensional incidence variety instead of a set of dimension<=1.

## Primary-source checks actually retrieved by root

- https://stacks.math.columbia.edu/tag/01V8 — smoothness from flatness, local finite presentation, and smooth fibers (not smooth fibers alone).
- https://stacks.math.columbia.edu/tag/01V9 — local fiberwise smoothness criterion with the flatness hypothesis.
- https://stacks.math.columbia.edu/tag/0529 — generic flatness over an integral/reduced base; finite-type hypotheses.

These tags were retrieved with search tools in the current turn, including independent primary-source search verification. Full mathematical derivations above are independent review, not quotations from those pages. Final module reviews must separately bind the actual final source hashes.

## Additional initial-range obstruction found independently by the setup reviewer

I checked the setup reviewer’s counterexample: P=G=Pcal=X=Spec(k[epsilon]/epsilon²), q=p=f=id, N=m=0. The initial flatness over k, smooth q, geometrically irreducible zero-dimensional nonempty fibers, and the zero-dimensional closed-subset nonemptiness axiom all hold. However Xcal_eta=Spec k is regular and reduced, while X is neither; the map Spec k to X is not flat. Thus the local-equivalence statements cannot all be transported from (2.1) through (2.11) under only the initial axioms. A sufficient repair for the needed regularity of h is that G is generically reduced: O_G,eta is then its function field and Spec k(eta)→G is a localization-type regular morphism, whose base change followed by the smooth q remains regular. This does not assert a full fresh review of all historical statements (2.1) through (2.11).

The later hypotheses P/k smooth and X/k smooth imply the respective total spaces are reduced, so the later proof can factor through G_red. That later argument proves smoothness of the generic section under the stated tangent-bad-set bound; it must not be mistaken for a proof of every two-sided local equivalence for arbitrary singular X. The recovered French phrase concerning (2.12) through (2.18) is preserved as the author's proposed scope with an explicit qualification.
