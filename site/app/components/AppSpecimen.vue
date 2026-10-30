<template>
	<!-- On large screens, after the first one, specimens flow in three lanes: columns 3 to 5, 6, and 7
	to 10. On tablets, the first two are on columns 1 to 3 and 4, the specimens of the third on rows of
	their own, after 03 on columns 5 to 6. Lanes are `contents` on phones, their specimens one flow, in
	the order of their notes -->
	<section class="relative layout pt-60">
		<h2 class="sr-only">Specimen</h2>

		<div class="group col-span-full mb-5 lg:col-start-3 lg:col-span-8">
			<SpecimenNote mark="01">50 italic, 20px</SpecimenNote>
			<SpecimenMark mark="01" class="block mb-2.5" />
			<!-- Over the lines -->
			<figure class="font-50 italic text-xl/tight lowercase">
				<blockquote lang="en" class="bg-paper">
					Of course it can always be improved, it can always be reimagined, it can always be
					approached from different perspectives. There’s no single version of things, and no idea
					is in any way finalized just because it was shown to the world. We can always go back, and
					we can always improve, and we can always change, and we can recreate, and that’s the
					spirit of nofinalversion.
				</blockquote>
				<figcaption class="bg-paper inline-block">
					Lidija Kacar,
					<cite
						><NuxtLink
							to="https://thoughts.nofinalversion.com/p/not-here-nor-there-first-exhibition"
							target="_blank"
							>nofinalversion</NuxtLink
						></cite
					>
				</figcaption>
			</figure>
		</div>

		<div
			class="contents md:grid md:grid-cols-subgrid md:col-span-3 md:content-start lg:col-start-3"
		>
			<figure class="group col-span-2 md:col-span-1 max-md:order-1 lowercase">
				<SpecimenNote mark="02">0 regular, 12px</SpecimenNote>
				<SpecimenMark mark="02" class="block mb-2.5" />
				<blockquote lang="fr">
					Puis, comme elle éprouvait au-dessus de sa tête la sensation d’un grand frôlement d’ailes,
					elle leva les yeux, elle s’arrêta à regarder les courroies, les longs rubans qui tendaient
					au plafond une gigantesque toile d’araignée, dont chaque fil se dévidait sans fin&nbsp;;
					le moteur à vapeur se cachait dans un coin, derrière un petit mur de briques&nbsp;; les
					courroies semblaient filer toutes seules, apporter le branle du fond de l’ombre, avec leur
					glissement continu, régulier, doux comme le vol d’un oiseau de nuit.
				</blockquote>
				<figcaption>
					Émile Zola,
					<cite
						><NuxtLink
							to="https://fr.wikisource.org/wiki/L%E2%80%99Assommoir/Chapitre_VI"
							target="_blank"
							>L’Assommoir</NuxtLink
						></cite
					>
				</figcaption>
			</figure>

			<SpecimenNikkei class="col-span-4 md:col-span-3 max-md:order-4 mt-40 md:mt-80" />
		</div>

		<div class="group col-span-2 md:col-span-1 lg:col-start-6 self-start max-md:order-3 md:mt-90">
			<SpecimenNote mark="04" class="md:justify-end">35 regular, 16px</SpecimenNote>
			<SpecimenMark mark="04" class="block mb-2.5 text-right" />
			<!-- Its height is the length of a line, lines go from right to left -->
			<figure
				lang="ja"
				class="w-fit max-w-full h-[52em] ml-auto md:h-[60.5em] writing-vertical font-35 text-base/tight bg-paper"
			>
				<blockquote>
					事実、「闇」を条件に入れなければ漆器の美しさは考えられないと云っていゝ。今日では白漆と云うようなものも出来たけれども、昔からある漆器の肌は、黒か、茶か、赤であって、それは幾重もの「闇」が堆積した色であり、周囲を包む暗黒の中から必然的に生れ出たもののように思える。派手な蒔絵などを施したピカピカ光る蝋塗りの手箱とか、文台とか、棚とかを見ると、いかにもケバケバしくて落ち着きがなく、俗悪にさえ思えることがあるけれども、もしそれらの器物を取り囲む空白を真っ黒な闇で塗り潰し、太陽や電燈の光線に代えるに一点の燈明か蝋燭のあかりにして見給え、忽ちそのケバケバしいものが底深く沈んで、渋い、重々しいものになるであろう。
				</blockquote>
				<figcaption>
					谷崎潤一郎<cite
						><NuxtLink to="https://www.aozora.gr.jp/cards/001383/card56642.html" target="_blank"
							>『陰翳礼讃』</NuxtLink
						></cite
					>
				</figcaption>
			</figure>
		</div>

		<div
			class="contents lg:grid lg:grid-cols-subgrid lg:col-start-7 lg:col-span-4 lg:content-start"
		>
			<div
				class="group col-span-2 md:max-lg:col-start-5 grid grid-cols-subgrid self-start max-md:order-2 mt-20"
			>
				<SpecimenNote
					mark="03"
					class="max-md:col-span-full md:max-lg:col-start-2 md:max-lg:row-start-1 md:max-lg:-ml-2.5"
					>50 bold, 52px<br />full-width</SpecimenNote
				>
				<p
					lang="ja"
					class="justify-self-end writing-vertical font-50 font-bold text-4xl lg:text-[3.25rem] tracking-[0.25em]"
				>
					２００６年１０月２４日、ＮＨＫ
				</p>
				<div
					class="md:max-lg:col-start-2 md:max-lg:row-start-1 md:max-lg:pt-[calc(1lh+0.3125rem)] -ml-2.5 flex flex-col gap-1.25"
				>
					<SpecimenMark mark="03" />
					<span class="flex-1 w-1.25 bg-ink" />
				</div>
			</div>

			<figure class="col-span-4 md:max-lg:col-start-3 max-md:order-5 mt-20 md:mt-5 lg:mt-70">
				<figcaption class="mb-2.5 font-35 text-right lowercase">specimen, blender cg</figcaption>
				<img
					src="/specimen/poster.webp"
					width="1600"
					height="1280"
					alt="A poster set in Kuronuri on a wall, 黒塗り over a pixelated red sun, above pangrams in Polish, Czech, and Hungarian"
					loading="lazy"
					class="w-full"
				/>
			</figure>

			<!-- Below large screens, the note is under the year, over the space left by the calendar -->
			<div
				class="group col-span-4 md:col-span-2 md:max-lg:col-start-5 grid grid-cols-[auto_auto] max-lg:grid-rows-[auto_1fr] justify-between items-start max-lg:relative max-md:order-6 mt-2.5"
			>
				<SpecimenNote mark="06" class="absolute max-lg:row-start-2 max-lg:w-max max-lg:mt-2.5"
					>mixed, 12px<br />enclosed cjk</SpecimenNote
				>
				<p
					lang="ja"
					class="pr-2.5 border-r-[0.3125rem] writing-vertical font-10 font-bold text-4xl lg:text-[3.25rem] tracking-[0.25em]"
				>
					１９９９年
				</p>
				<SpecimenCalendar class="max-lg:row-span-2" />
			</div>
		</div>
	</section>
</template>
