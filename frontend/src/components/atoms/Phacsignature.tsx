import React from 'react'

type PhacsignatureConfig = {
  lang?: 'en' | 'fr'
  textColor?: 'black' | 'white'
  variant?: 'color' | 'monochrome' // monochrome make the flag color the same as the textColor - color renders a red flag (this ensures only the 4 options from anada.ca/en/treasury-board-secretariat/services/government-communications/design-standard/colour-design-standard-fip.html#toc1 can be used )
  width?: string,
}

type EnglishGovGouvProps = {
  textColor?: 'black' | 'white'
  flagColor?: '#EA2D37'
}

type FrenchGovGouvProps = {
  textColor?: 'black' | 'white'
  flagColor?: '#EA2D37'
}

const FrenchGovGouv = ({ textColor = 'black', flagColor = '#EA2D37' }: FrenchGovGouvProps) => {
  return (

    <svg
      version="1.1"
      xmlns="http://www.w3.org/2000/svg"
      viewBox="150 0 275 35"
      width='350px'
      preserveAspectRatio="xMinYMin meet"
      role="img"
      aria-label="PHAC Logo with Canadian flag - Logo de la ASPC avec Drapeau Canadien" // may need to explore aria more in the future 
    >

      <g id="558" fill={textColor}
      >
        <svg
          version="1.1"
          xmlns="http://www.w3.org/2000/svg"
          width="100%"
          height="100%"
          viewBox="-160 0 143 34"
          preserveAspectRatio="xMinYMin meet"
          // This fill element was parametrized relative to the original svg.
          fill={flagColor}
        >
          <g id="557" fill={flagColor}
          >
            <path
              d="M 6.2144e-4,0.24964784 H 14.743837 V 30.363217 H 6.2144e-4 Z"
              id="path160" /><path
              d="m 30.388,28.056351 c 0,0 -0.129828,-5.0413 -0.129828,-5.417582 0,-0.50391 0.253055,-0.624936 0.756965,-0.50391 0.50391,0 5.039099,0.880192 5.039099,0.880192 0,0 -0.123227,-0.880192 -0.501709,-1.637157 -0.125428,-0.877992 0,-1.005619 0.378482,-1.131047 0.123227,-0.129828 5.164527,-4.535189 5.164527,-4.535189 l -1.00782,-0.50611 c -0.253055,-0.125428 -0.253055,-0.629338 -0.253055,-1.00782 0,-0.129829 0.882392,-3.274315 0.882392,-3.274315 0,0 -2.143267,0.629338 -2.642776,0.629338 -0.506111,0 -0.631538,0 -0.759166,-0.253055 0,-0.50391 -0.629337,-1.6371576 -0.629337,-1.6371576 0,0 -2.52175,3.0234596 -2.642777,3.0234596 -0.50611,0.50391 -1.01002,0 -1.01002,-0.50171 0.125427,-0.50831 1.384102,-6.4276016 1.384102,-6.4276016 0,0 -1.384102,0.7569651 -1.890212,1.1354477 C 32.148384,7.1407883 31.772102,7.0175614 31.646675,6.5136515 31.268192,6.2649973 29.758663,2.61 29.758663,2.61 c 0,0 -1.766986,3.6549973 -1.892413,3.9036515 -0.380683,0.5039099 -0.50391,0.6271368 -1.133247,0.3784826 -0.50391,-0.3784826 -1.890213,-1.1354477 -1.890213,-1.1354477 0,0 1.260875,5.9192916 1.386303,6.4276016 0,0.50171 -0.253055,1.00562 -0.882393,0.50171 L 22.701723,9.6625384 c 0,0 -0.50611,1.1332476 -0.631537,1.6371576 -0.253056,0.253055 -0.50391,0.253055 -0.882393,0.253055 -0.376282,0 -2.772605,-0.629338 -2.772605,-0.629338 0,0 0.882393,3.144486 1.135448,3.274315 0.125427,0.378482 0.125427,0.882392 -0.50611,1.00782 l -0.629338,0.50611 c 0,0 5.0413,4.405361 5.0413,4.535189 0.253055,0.125428 0.629337,0.253055 0.253055,1.131047 a 24.975448,24.975448 0 0 1 -0.631538,1.637157 c 0,0 4.913672,-0.880192 5.419783,-0.880192 0.499509,-0.121026 0.754764,0 0.754764,0.50391 0,0.376282 -0.125427,5.417582 -0.125427,5.417582 z"
              id="path162" /><path
              d="M 59.494272,0.24964784 H 44.498001 V 30.365417 h 14.996271 z"
              id="path164" />
          </g>
        </svg>
        <path
          d="m 248.672,12.648096 h 2.24009 l 1.15525,-3.2677126 h 4.93348 l 1.16185,3.2677126 h 2.31931 L 255.72014,0.288 h -2.2973 z m 5.85328,-10.2256304 h 0.0528 l 1.8528,5.3075578 h -3.77382 z"
          id="path218" /><path
          d="m 269.175,3.7071259 h -1.97163 v 1.2300683 h -0.0374 c -0.49951,-1.0078198 -1.52053,-1.4721211 -2.64498,-1.4721211 -2.54595,0 -4.04888,2.0728522 -4.04888,4.4823778 0,2.5591581 1.17286,4.7046261 4.01368,4.7046261 1.10464,0 2.12786,-0.583127 2.68018,-1.575544 h 0.0374 v 1.3753 c 0,1.467721 -0.70855,2.284099 -2.3017,2.284099 -1.00562,0 -1.90342,-0.187041 -2.14987,-1.311486 h -1.97163 c 0.17164,2.090456 2.20048,2.783607 4.00047,2.783607 2.81882,0 4.39436,-1.333491 4.39436,-4.020277 z m -4.37896,7.3914121 c -1.64375,0 -2.35671,-1.4897247 -2.35671,-2.9574449 0,-1.4919254 0.60733,-3.1224811 2.35671,-3.1224811 1.71418,0 2.40733,1.4215101 2.40733,2.966247 0,1.5161308 -0.66234,3.113679 -2.40733,3.113679"
          id="path220" /><path
          d="m 272.226,7.3858549 c 0.055,-1.3334909 0.98582,-2.369917 2.35451,-2.369917 1.33349,0 2.18068,1.1244453 2.24889,2.369917 z m 6.57723,1.3004837 c 0.32788,-2.6801847 -1.3995,-5.22614 -4.22272,-5.22614 -2.66698,0 -4.33054,2.1806756 -4.33054,4.726631 0,2.7483994 1.57774,4.7068264 4.38336,4.7068264 1.95402,0 3.61538,-1.089237 4.05328,-3.0432635 h -1.87481 c -0.34768,0.9792135 -1.03863,1.4809235 -2.17847,1.4809235 -1.64596,0 -2.40733,-1.241071 -2.40733,-2.6449774 z"
          id="path222" /><path
          d="m 279.826,12.656204 h 1.97603 V 7.3794534 c 0,-1.3180875 0.84719,-2.356714 2.16087,-2.356714 1.16186,0 1.71418,0.6073324 1.75158,2.0090382 v 5.6244264 h 1.97163 V 6.5124643 c 0,-2.0068377 -1.22786,-3.0454643 -3.16649,-3.0454643 -1.17505,0 -2.20048,0.605132 -2.788,1.595348 l -0.0308,-0.039609 V 3.7112533 H 279.826 Z"
          id="path224" /><path
          d="m 297.298,6.7001539 c -0.18924,-2.1982795 -1.95623,-3.2369061 -4.03128,-3.2369061 -2.94424,0 -4.41636,2.1124608 -4.41636,4.8124498 0,2.6295734 1.53813,4.6232084 4.34374,4.6232084 2.30611,0 3.73862,-1.28288 4.1039,-3.6043862 h -1.96943 c -0.19364,1.2828802 -0.99022,2.0420452 -2.13447,2.0420452 -1.70977,0 -2.36771,-1.5777439 -2.36771,-3.0608674 0,-2.7153923 1.43251,-3.2567104 2.45573,-3.2567104 1.09584,0 1.88802,0.5897286 2.04645,1.6811667 z"
          id="path226" /><path
          d="m 299.966,7.3858549 c 0.055,-1.3334909 0.98582,-2.369917 2.35451,-2.369917 1.33349,0 2.18508,1.1244453 2.2533,2.369917 z m 6.58164,1.3004837 c 0.32347,-2.6801847 -1.40171,-5.22614 -4.22713,-5.22614 -2.66478,0 -4.32394,2.1806756 -4.32394,4.726631 0,2.7483994 1.57334,4.7068264 4.37676,4.7068264 1.95622,0 3.61978,-1.089237 4.05328,-3.0432635 h -1.87041 c -0.34767,0.9792135 -1.03863,1.4809235 -2.18287,1.4809235 -1.64376,0 -2.40733,-1.241071 -2.40733,-2.6449774 z"
          id="path228" /><path
          d="m 321.296,0.28945008 h -1.97383 V 4.864248 h -0.033 c -0.60953,-0.990216 -1.855,-1.4039062 -2.97945,-1.4039062 -1.95622,0 -3.87724,1.4193096 -3.87724,4.6606166 0,2.6757836 1.3687,4.7750416 4.18531,4.7750416 1.12885,0 2.25329,-0.435695 2.7726,-1.452317 h 0.033 v 1.205863 h 1.87261 z m -6.8919,7.98334142 c 0,-1.6085509 0.66014,-3.2567104 2.50854,-3.2567104 1.52714,0 2.47774,1.1728559 2.47774,3.1510874 0,1.5579398 -0.74596,3.1664905 -2.50854,3.1664905 -1.71418,0 -2.47774,-1.518331 -2.47774,-3.0608675"
          id="path230" /><path
          d="m 324.502,7.3858549 c 0.0506,-1.3334909 0.98582,-2.369917 2.35451,-2.369917 1.33349,0 2.18068,1.1244453 2.2533,2.369917 z m 6.58164,1.3004837 c 0.32347,-2.6801847 -1.40611,-5.22614 -4.22713,-5.22614 -2.66478,0 -4.32834,2.1806756 -4.32834,4.726631 0,2.7483994 1.57554,4.7068264 4.38116,4.7068264 1.95402,0 3.61538,-1.089237 4.04888,-3.0432635 h -1.86601 c -0.34988,0.9792135 -1.04303,1.4809235 -2.18287,1.4809235 -1.64596,0 -2.40733,-1.241071 -2.40733,-2.6449774 z"
          id="path232" /><path
          d="m 337.79631,0.29011088 h 1.97383 V 12.650207 h -1.97383 z"
          id="path234" /><path
          d="m 348.934,6.0608731 c 0,-1.8858113 -1.8396,-2.5921654 -3.58458,-2.5921654 -1.97383,0 -3.93006,0.6733469 -4.07089,2.9750489 h 1.97383 c 0.088,-0.9660107 0.86699,-1.42151 1.97383,-1.42151 0.79657,0 1.85281,0.1936422 1.85281,1.2146649 0,1.1574525 -1.26528,1.0034189 -2.68239,1.2586746 -1.66136,0.1914417 -3.44815,0.5567214 -3.44815,2.7902089 0,1.751582 1.45672,2.61637 3.06747,2.61637 1.05403,0 2.3193,-0.332272 3.10047,-1.089237 0.15404,0.811977 0.72176,1.089237 1.52054,1.089237 0.32787,0 0.9528,-0.116625 1.24767,-0.224449 v -1.368698 c -0.20685,0.03081 -0.36308,0.03081 -0.48411,0.03081 -0.36528,0 -0.4665,-0.184841 -0.4665,-0.671147 z m -1.97383,3.5845819 c 0,1.245472 -1.3533,1.69437 -2.21808,1.69437 -0.69096,0 -1.8154,-0.257457 -1.8154,-1.142049 0,-1.0364266 0.75917,-1.3466942 1.60855,-1.4919259 0.86479,-0.1474322 1.8154,-0.1342293 2.42493,-0.5325162 z"
          id="path236" /><path
          d="m 355.044,9.7794979 c 0.0308,2.1124611 1.70977,3.1180801 3.96086,3.1180801 1.85281,0 3.99828,-0.78117 3.99828,-2.906834 0,-1.7669854 -1.45232,-2.2929002 -2.88923,-2.6163707 -1.45452,-0.3322725 -2.90904,-0.4709027 -2.90904,-1.4369135 0,-0.7811704 1.05623,-0.9198006 1.62616,-0.9198006 0.86699,0 1.64816,0.2574562 1.81759,1.1970611 h 2.06405 c -0.24645,-1.9936349 -1.90341,-2.7528005 -3.74301,-2.7528005 -1.62836,0 -3.73862,0.605132 -3.73862,2.5635592 0,1.8175965 1.42151,2.3391103 2.87163,2.644977 1.44131,0.334473 2.87602,0.4488979 2.92664,1.491925 0.0528,1.018823 -1.24328,1.172856 -1.98704,1.172856 -1.06063,0 -1.92322,-0.41369 -2.02884,-1.5557391 z"
          id="path238" /><path
          d="m 371.52,6.0608731 c 0,-1.8858113 -1.8352,-2.5921654 -3.58018,-2.5921654 -1.97163,0 -3.93006,0.6733469 -4.06429,2.9750489 h 1.96943 c 0.0858,-0.9660107 0.86699,-1.42151 1.97383,-1.42151 0.79878,0 1.85281,0.1936422 1.85281,1.2146649 0,1.1574525 -1.26308,1.0034189 -2.68019,1.2586746 -1.66576,0.1914417 -3.44595,0.5567214 -3.44595,2.7902089 0,1.751582 1.45012,2.61637 3.05867,2.61637 1.05623,0 2.3237,-0.332272 3.10267,-1.089237 0.15404,0.811977 0.72616,1.089237 1.52494,1.089237 0.32347,0 0.9506,-0.116625 1.24327,-0.224449 v -1.368698 c -0.20465,0.03081 -0.36088,0.03081 -0.48191,0.03081 -0.36748,0 -0.4731,-0.184841 -0.4731,-0.671147 z m -1.97163,3.5845819 c 0,1.245472 -1.34889,1.69437 -2.21368,1.69437 -0.69095,0 -1.8176,-0.257457 -1.8176,-1.142049 0,-1.0364266 0.76357,-1.3466942 1.61295,-1.4919259 0.86259,-0.1474322 1.8132,-0.1342293 2.41833,-0.5325162 z"
          id="path240" /><path
          d="m 373.52,12.656204 h 1.97383 V 7.3794534 c 0,-1.3180875 0.84719,-2.356714 2.16307,-2.356714 1.15966,0 1.71198,0.6073324 1.74938,2.0090382 v 5.6244264 h 1.97383 V 6.5124643 c 0,-2.0068377 -1.23006,-3.0454643 -3.16869,-3.0454643 -1.17945,0 -2.19828,0.605132 -2.79021,1.595348 l -0.0308,-0.039609 V 3.7112533 H 373.52 Z"
          id="path242" /><path
          d="m 382.076,5.183256 h 1.48312 v 5.278952 c 0.0374,1.489724 0.4203,2.286298 2.47774,2.286298 0.4313,0 0.84939,-0.07042 1.28288,-0.105623 v -1.524932 c -0.27726,0.07042 -0.55452,0.07042 -0.82958,0.07042 -0.88459,0 -0.9528,-0.415891 -0.9528,-1.2278679 V 5.183256 h 1.78238 V 3.7111349 h -1.78238 V 1.0287498 h -1.97824 V 3.7111349 H 382.076 Z"
          id="path244" /><path
          d="m 389.801,7.3954104 c 0.0484,-1.3334909 0.98802,-2.369917 2.35011,-2.369917 1.33349,0 2.18288,1.1244453 2.25109,2.369917 z m 6.57723,1.3004837 c 0.32788,-2.6801847 -1.4017,-5.22614 -4.22712,-5.22614 -2.66258,0 -4.32614,2.1806757 -4.32614,4.726631 0,2.7483999 1.57554,4.7068269 4.38115,4.7068269 1.95403,0 3.61759,-1.089238 4.04889,-3.043264 H 394.389 c -0.34768,0.979214 -1.03863,1.480923 -2.18288,1.480923 -1.64595,0 -2.40512,-1.241071 -2.40512,-2.6449769 z M 390.734,2.4773376 h 1.43472 l 2.45793,-2.47113904 h -2.33471 z"
          id="path246" /><path
          d="m 249.888,33.840328 h 1.97383 v -4.473576 h 0.0352 c 0.62053,0.992416 1.8506,1.406107 2.99705,1.406107 2.64498,0 3.85744,-2.270896 3.85744,-4.67602 0,-2.618571 -1.3687,-4.761839 -4.18751,-4.761839 -1.14205,0 -2.22028,0.431294 -2.7704,1.456718 h -0.0352 V 21.581454 H 249.888 Z m 6.8919,-7.778697 c 0,1.55794 -0.67554,3.144486 -2.47554,3.144486 -1.59314,0 -2.51074,-1.342293 -2.51074,-3.144486 0,-1.903415 0.84498,-3.173092 2.51074,-3.173092 1.62616,0 2.47554,1.549138 2.47554,3.173092"
          id="path248" /><path
          d="m 267.79,21.572595 h -1.97383 v 5.193133 c 0,1.384102 -0.55232,2.433731 -2.20048,2.433731 -1.07383,0 -1.71417,-0.565524 -1.71417,-2.141067 v -5.485797 h -1.97384 v 5.675038 c 0,2.33911 1.00782,3.516367 3.34473,3.516367 0.98362,0 2.05965,-0.591929 2.54376,-1.487524 h 0.0308 v 1.245471 H 267.79 Z"
          id="path250" /><path
          d="m 269.44,30.529244 h 1.87041 v -1.232269 h 0.033 c 0.58972,1.179457 1.88801,1.474322 3.09827,1.474322 2.65158,0 3.86184,-2.268695 3.86184,-4.67602 0,-2.616371 -1.3687,-4.759639 -4.18751,-4.759639 -1.00782,0 -2.13227,0.536918 -2.66698,1.399506 h -0.0352 V 18.166947 H 269.44 Z m 6.8897,-4.469175 c 0,1.55794 -0.67554,3.146686 -2.47554,3.146686 -1.59535,0 -2.51074,-1.342292 -2.51074,-3.146686 0,-1.903415 0.84938,-3.170892 2.51074,-3.170892 1.63056,0 2.47554,1.546938 2.47554,3.170892"
          id="path252" /><path
          d="m 279.532,18.163812 h 1.97603 V 30.526109 H 279.532 Z"
          id="path254" /><path
          d="m 283.2244,20.03422 h 1.97383 v -1.870408 h -1.97383 z m 0,10.489688 h 1.97383 v -8.949352 h -1.97383 z"
          id="path256" /><path
          d="m 295.296,21.57958 h -1.87261 v 1.210264 h -0.033 c -0.55232,-1.025424 -1.62835,-1.456718 -2.7704,-1.456718 -2.81881,0 -4.18751,2.145468 -4.18751,4.761839 0,2.405124 1.21466,4.67602 3.85964,4.67602 1.14205,0 2.37212,-0.413691 2.99485,-1.406107 h 0.0352 v 4.473576 h 1.97383 z m -6.8897,4.480177 c 0,-1.623954 0.84498,-3.170892 2.47334,-3.170892 1.64816,0 2.51074,1.238871 2.51074,3.170892 0,1.874809 -0.79657,3.146686 -2.51074,3.146686 -1.8022,0 -2.47334,-1.588746 -2.47334,-3.146686"
          id="path258" /><path
          d="m 304.82,21.572595 h -1.97383 v 5.193133 c 0,1.384102 -0.55452,2.433731 -2.20048,2.433731 -1.07383,0 -1.71417,-0.565524 -1.71417,-2.141067 v -5.485797 h -1.97384 v 5.675038 c 0,2.33911 1.00782,3.516367 3.34253,3.516367 0.98582,0 2.06185,-0.591929 2.54596,-1.487524 h 0.0352 v 1.245471 H 304.82 Z"
          id="path260" /><path
          d="m 307.956,25.260456 c 0.0528,-1.333491 0.98802,-2.374318 2.35671,-2.374318 1.33129,0 2.18068,1.131047 2.24889,2.374318 z m 6.57944,1.296083 c 0.33007,-2.680185 -1.40391,-5.22614 -4.22273,-5.22614 -2.66478,0 -4.33054,2.178475 -4.33054,4.724431 0,2.755001 1.57554,4.711227 4.38116,4.711227 1.95842,0 3.61758,-1.089237 4.05108,-3.052065 H 312.544 c -0.34768,0.992416 -1.03863,1.489724 -2.18067,1.489724 -1.64156,0 -2.40733,-1.243271 -2.40733,-2.647177 z"
          id="path262" /><path
          d="m 329.284,18.159651 h -1.97383 v 4.565996 h -0.033 c -0.60953,-0.981415 -1.8572,-1.399506 -2.97945,-1.399506 -1.95622,0 -3.87724,1.42151 -3.87724,4.656216 0,2.684586 1.3687,4.781643 4.18751,4.781643 1.12665,0 2.25109,-0.433495 2.7704,-1.456718 h 0.0352 v 1.214665 h 1.87041 z m -6.8919,7.981141 c 0,-1.612952 0.66014,-3.261112 2.51074,-3.261112 1.52494,0 2.47554,1.183858 2.47554,3.155488 0,1.560141 -0.74596,3.16209 -2.51074,3.16209 -1.70978,0 -2.47554,-1.518331 -2.47554,-3.056466"
          id="path264" /><path
          d="m 338.81,21.572595 h -1.97383 v 5.193133 c 0,1.384102 -0.55672,2.433731 -2.20048,2.433731 -1.06943,0 -1.71197,-0.565524 -1.71197,-2.141067 v -5.485797 h -1.97383 v 5.675038 c 0,2.33911 1.00561,3.516367 3.34032,3.516367 0.98582,0 2.05965,-0.591929 2.54596,-1.487524 h 0.033 v 1.245471 H 338.81 Z"
          id="path266" /><path
          d="m 356.485,22.094016 c -0.26186,-2.66038 -2.45794,-4.198516 -5.24814,-4.220521 -3.70341,0 -5.9193,2.944243 -5.9193,6.471612 0,3.533971 2.21589,6.480414 5.9193,6.480414 2.99705,0 5.08971,-2.046447 5.26134,-5.008293 h -2.11026 c -0.17604,1.802193 -1.22787,3.234706 -3.15108,3.234706 -2.64718,0 -3.75402,-2.33471 -3.75402,-4.706827 0,-2.369917 1.10684,-4.704626 3.75402,-4.704626 1.80219,0 2.71759,1.038626 3.08287,2.453535 z"
          id="path268" /><path
          d="m 365.212,23.927675 c 0,-1.885811 -1.8374,-2.598767 -3.58458,-2.598767 -1.97383,0 -3.92786,0.677748 -4.06869,2.981651 h 1.97383 c 0.088,-0.972613 0.86919,-1.425911 1.97383,-1.425911 0.79658,0 1.85501,0.193642 1.85501,1.219065 0,1.157453 -1.26748,0.999018 -2.68459,1.260875 -1.66136,0.189242 -3.44595,0.552321 -3.44595,2.790209 0,1.744981 1.45232,2.61197 3.06527,2.61197 1.05403,0 2.3193,-0.325671 3.09607,-1.089238 0.15844,0.809777 0.72836,1.089238 1.52494,1.089238 0.32787,0 0.9528,-0.118826 1.24767,-0.224449 v -1.370899 c -0.20905,0.03081 -0.36528,0.03081 -0.48631,0.03081 -0.36528,0 -0.4665,-0.187041 -0.4665,-0.673347 z m -1.97383,3.584582 c 0,1.243271 -1.3511,1.689969 -2.21808,1.689969 -0.68875,0 -1.8154,-0.253056 -1.8154,-1.131047 0,-1.043028 0.76357,-1.359897 1.61295,-1.491926 0.86039,-0.160635 1.8154,-0.14083 2.42053,-0.541318 z"
          id="path270" /><path
          d="m 366.857,30.528605 h 1.97823 v -5.285553 c 0,-1.311486 0.84719,-2.354513 2.16307,-2.354513 1.15966,0 1.70978,0.609533 1.74718,2.01564 v 5.624426 h 1.97384 v -6.14594 c 0,-2.011239 -1.23007,-3.047665 -3.1687,-3.047665 -1.17725,0 -2.19828,0.602932 -2.7858,1.593148 l -0.0352,-0.03961 V 21.579253 H 366.857 Z"
          id="path272" /><path
          d="m 383.81,23.927675 c 0,-1.885811 -1.833,-2.598767 -3.58238,-2.598767 -1.97603,0 -3.93006,0.677748 -4.06869,2.981651 h 1.97383 c 0.088,-0.972613 0.86259,-1.425911 1.97383,-1.425911 0.79438,0 1.85281,0.193642 1.85281,1.219065 0,1.157453 -1.26748,0.999018 -2.68459,1.260875 -1.66136,0.189242 -3.44595,0.552321 -3.44595,2.790209 0,1.744981 1.45452,2.61197 3.06307,2.61197 1.05623,0 2.3259,-0.325671 3.10267,-1.089238 0.15184,0.809777 0.72396,1.089238 1.52054,1.089238 0.32787,0 0.9528,-0.118826 1.24987,-0.224449 v -1.370899 c -0.21125,0.03081 -0.36748,0.03081 -0.48851,0.03081 -0.36528,0 -0.4665,-0.187041 -0.4665,-0.673347 z m -1.97383,3.584582 c 0,1.243271 -1.3511,1.689969 -2.21368,1.689969 -0.69315,0 -1.8198,-0.253056 -1.8198,-1.131047 0,-1.043028 0.76357,-1.359897 1.61295,-1.491926 0.86039,-0.160635 1.8176,-0.14083 2.42053,-0.541318 z"
          id="path274" /><path
          d="m 393.89,18.159651 h -1.97603 v 4.565996 h -0.033 c -0.60733,-0.981415 -1.8506,-1.399506 -2.97725,-1.399506 -1.95842,0 -3.87504,1.42151 -3.87504,4.656216 0,2.684586 1.36429,4.781643 4.18531,4.781643 1.12445,0 2.25109,-0.433495 2.7726,-1.456718 h 0.0308 v 1.214665 H 393.89 Z m -6.8897,7.981141 c 0,-1.612952 0.65794,-3.261112 2.51074,-3.261112 1.52274,0 2.47554,1.183858 2.47554,3.155488 0,1.560141 -0.74596,3.16209 -2.51074,3.16209 -1.71418,0 -2.47554,-1.518331 -2.47554,-3.056466"
          id="path276" /><path
          d="m 403.05,23.927675 c 0,-1.885811 -1.8374,-2.598767 -3.58458,-2.598767 -1.97383,0 -3.92786,0.677748 -4.06869,2.981651 h 1.97383 c 0.088,-0.972613 0.86479,-1.425911 1.97603,-1.425911 0.79438,0 1.84841,0.193642 1.84841,1.219065 0,1.157453 -1.26308,0.999018 -2.68239,1.260875 -1.66136,0.189242 -3.44375,0.552321 -3.44375,2.790209 0,1.744981 1.45232,2.61197 3.06307,2.61197 1.05623,0 2.3193,-0.325671 3.10047,-1.089238 0.15624,0.809777 0.72616,1.089238 1.52274,1.089238 0.32787,0 0.9506,-0.118826 1.24547,-0.224449 v -1.370899 c -0.20685,0.03081 -0.36308,0.03081 -0.48411,0.03081 -0.36308,0 -0.4665,-0.187041 -0.4665,-0.673347 z m -1.97383,3.584582 c 0,1.243271 -1.3511,1.689969 -2.21588,1.689969 -0.69095,0 -1.8176,-0.253056 -1.8176,-1.131047 0,-1.043028 0.75917,-1.359897 1.61295,-1.491926 0.86039,-0.160635 1.811,-0.14083 2.42053,-0.541318 z"
          id="path278" />
      </g>
    </svg>
  )
}
const EnglishGovGouv = ({ textColor = 'black', flagColor = '#EA2D37' }: EnglishGovGouvProps) => {
  return (
    <svg
      version="1.1"
      xmlns="http://www.w3.org/2000/svg"
      viewBox="-15 0 275 35"
      width='350px'
      preserveAspectRatio="xMinYMin meet"
      role="img"
      aria-label="PHAC Logo with Canadian flag - Logo de la ASPC avec Drapeau Canadien" // may need to explore aria more in the future 
    >

      <g id="g560" fill={textColor}>
        <svg
          version="1.1"
          xmlns="http://www.w3.org/2000/svg"
          width="100%"
          height="100%"
          viewBox="0 0 143 34"
          preserveAspectRatio="xMinYMin meet"
          // This fill element was parametrized relative to the original svg.
          fill={flagColor}
        >
          <g id="557" fill={flagColor}
          >
            <path
              d="M 6.2144e-4,0.24964784 H 14.743837 V 30.363217 H 6.2144e-4 Z"
              id="path160" /><path
              d="m 30.388,28.056351 c 0,0 -0.129828,-5.0413 -0.129828,-5.417582 0,-0.50391 0.253055,-0.624936 0.756965,-0.50391 0.50391,0 5.039099,0.880192 5.039099,0.880192 0,0 -0.123227,-0.880192 -0.501709,-1.637157 -0.125428,-0.877992 0,-1.005619 0.378482,-1.131047 0.123227,-0.129828 5.164527,-4.535189 5.164527,-4.535189 l -1.00782,-0.50611 c -0.253055,-0.125428 -0.253055,-0.629338 -0.253055,-1.00782 0,-0.129829 0.882392,-3.274315 0.882392,-3.274315 0,0 -2.143267,0.629338 -2.642776,0.629338 -0.506111,0 -0.631538,0 -0.759166,-0.253055 0,-0.50391 -0.629337,-1.6371576 -0.629337,-1.6371576 0,0 -2.52175,3.0234596 -2.642777,3.0234596 -0.50611,0.50391 -1.01002,0 -1.01002,-0.50171 0.125427,-0.50831 1.384102,-6.4276016 1.384102,-6.4276016 0,0 -1.384102,0.7569651 -1.890212,1.1354477 C 32.148384,7.1407883 31.772102,7.0175614 31.646675,6.5136515 31.268192,6.2649973 29.758663,2.61 29.758663,2.61 c 0,0 -1.766986,3.6549973 -1.892413,3.9036515 -0.380683,0.5039099 -0.50391,0.6271368 -1.133247,0.3784826 -0.50391,-0.3784826 -1.890213,-1.1354477 -1.890213,-1.1354477 0,0 1.260875,5.9192916 1.386303,6.4276016 0,0.50171 -0.253055,1.00562 -0.882393,0.50171 L 22.701723,9.6625384 c 0,0 -0.50611,1.1332476 -0.631537,1.6371576 -0.253056,0.253055 -0.50391,0.253055 -0.882393,0.253055 -0.376282,0 -2.772605,-0.629338 -2.772605,-0.629338 0,0 0.882393,3.144486 1.135448,3.274315 0.125427,0.378482 0.125427,0.882392 -0.50611,1.00782 l -0.629338,0.50611 c 0,0 5.0413,4.405361 5.0413,4.535189 0.253055,0.125428 0.629337,0.253055 0.253055,1.131047 a 24.975448,24.975448 0 0 1 -0.631538,1.637157 c 0,0 4.913672,-0.880192 5.419783,-0.880192 0.499509,-0.121026 0.754764,0 0.754764,0.50391 0,0.376282 -0.125427,5.417582 -0.125427,5.417582 z"
              id="path162" /><path
              d="M 59.494272,0.24964784 H 44.498001 V 30.365417 h 14.996271 z"
              id="path164" />
          </g>
        </svg>
        <path
          d="m 84.908,12.648096 h 2.160871 V 7.9280666 h 3.291918 c 3.52957,0.015403 4.207318,-2.2730959 4.207318,-3.8024295 C 94.568107,2.5764992 93.890359,0.288 90.360789,0.288 H 84.908 Z M 87.068871,2.0593864 h 3.2061 c 1.142049,0 2.127864,0.4092893 2.127864,2.0486469 0,1.5645413 -1.197061,2.0464464 -2.165272,2.0464464 h -3.168692 z"
          id="path166" /><path
          d="m 103.554,3.704595 h -1.97163 v 5.1909324 c 0,1.3841016 -0.55452,2.4381316 -2.202681,2.4381316 -1.073834,0 -1.711973,-0.567724 -1.711973,-2.1432673 V 3.704595 h -1.973831 v 5.6772384 c 0,2.3369096 1.00562,3.5141666 3.34253,3.5141666 0.983615,0 2.059645,-0.591929 2.545955,-1.489725 h 0.033 v 1.243271 h 1.93862 z"
          id="path168" /><path
          d="m 105.202,12.653642 h 1.87041 v -1.227867 h 0.033 c 0.58972,1.175056 1.88801,1.474321 3.09827,1.474321 2.64938,0 3.86184,-2.270895 3.86184,-4.6738194 0,-2.6163707 -1.3687,-4.7618387 -4.18751,-4.7618387 -1.00782,0 -2.13006,0.5369171 -2.66698,1.4039063 h -0.0352 V 0.29354624 H 105.202 Z m 6.8919,-4.462573 c 0,1.5579398 -0.67554,3.146686 -2.47774,3.146686 -1.59314,0 -2.51074,-1.3422924 -2.51074,-3.146686 0,-1.9056157 0.84938,-3.1708917 2.51074,-3.1708917 1.63056,0 2.47774,1.540336 2.47774,3.1708917"
          id="path170" /><path
          d="m 115.30137,0.29011088 h 1.96723 V 12.650207 h -1.96723 z"
          id="path172" /><path
          d="m 118.98938,2.1605189 h 1.97383 V 0.29011088 h -1.97383 z m 0,10.4896881 h 1.97383 V 3.7052558 h -1.97383 z"
          id="path174" /><path
          d="m 130.644,6.7001539 c -0.19364,-2.1982795 -1.95403,-3.2369061 -4.03568,-3.2369061 -2.93984,0 -4.41196,2.1124608 -4.41196,4.8124498 0,2.6295734 1.54033,4.6232084 4.34374,4.6232084 2.30171,0 3.74082,-1.28288 4.1039,-3.6043862 h -1.97603 c -0.19144,1.2828802 -0.98582,2.0420452 -2.12787,2.0420452 -1.71417,0 -2.36991,-1.5777439 -2.36991,-3.0608674 0,-2.7153923 1.43471,-3.2567104 2.45793,-3.2567104 1.08924,0 1.88582,0.5897286 2.03985,1.6811667 z"
          id="path176" /><path
          d="m 137.288,12.648096 h 2.16527 V 7.0764808 h 5.62443 v 5.5716152 h 2.16307 V 0.288 h -2.16307 v 4.9202733 h -5.62443 V 0.288 H 137.288 Z"
          id="path178" /><path
          d="m 150.624,7.3858549 c 0.0484,-1.3334909 0.98582,-2.369917 2.35231,-2.369917 1.33569,0 2.18068,1.1244453 2.25109,2.369917 z m 6.57723,1.3004837 c 0.33008,-2.6801847 -1.4017,-5.22614 -4.22492,-5.22614 -2.66478,0 -4.32834,2.1806756 -4.32834,4.726631 0,2.7483994 1.57554,4.7068264 4.38115,4.7068264 1.95623,0 3.61979,-1.089237 4.05109,-3.0432635 h -1.86601 c -0.35208,0.9792135 -1.04303,1.4809235 -2.18508,1.4809235 -1.64375,0 -2.40512,-1.241071 -2.40512,-2.6449774 z"
          id="path180" /><path
          d="m 165.72,6.0608731 c 0,-1.8858113 -1.8352,-2.5921654 -3.58018,-2.5921654 -1.97163,0 -3.93006,0.6733469 -4.07089,2.9750489 h 1.97383 c 0.088,-0.9660107 0.86699,-1.42151 1.97383,-1.42151 0.80098,0 1.85281,0.1936422 1.85281,1.2146649 0,1.1574525 -1.26528,1.0034189 -2.68459,1.2586746 -1.65916,0.1914417 -3.44595,0.5567214 -3.44595,2.7902089 0,1.751582 1.45672,2.61637 3.06527,2.61637 1.05623,0 2.3237,-0.332272 3.10267,-1.089237 0.15404,0.811977 0.72616,1.089237 1.52274,1.089237 0.32567,0 0.9506,-0.116625 1.24547,-0.224449 v -1.368698 c -0.20905,0.03081 -0.36308,0.03081 -0.48631,0.03081 -0.36088,0 -0.4687,-0.184841 -0.4687,-0.671147 z m -1.97163,3.5845819 c 0,1.245472 -1.35109,1.69437 -2.21588,1.69437 -0.69315,0 -1.8176,-0.257457 -1.8176,-1.142049 0,-1.0364266 0.76137,-1.3466942 1.61075,-1.4919259 0.86699,-0.1474322 1.8176,-0.1342293 2.42273,-0.5325162 z"
          id="path182" /><path
          d="m 167.42194,0.29011088 h 1.97163 V 12.650207 h -1.97163 z"
          id="path184" /><path
          d="m 170.161,5.183256 h 1.48752 v 5.278952 c 0.0352,1.489724 0.4181,2.286298 2.47334,2.286298 0.4335,0 0.84939,-0.07042 1.28288,-0.105623 v -1.524932 c -0.27506,0.07042 -0.55452,0.07042 -0.82738,0.07042 -0.88679,0 -0.955,-0.415891 -0.955,-1.2278679 V 5.183256 h 1.78238 V 3.7111349 h -1.78238 V 1.0287498 h -1.97384 V 3.7111349 H 170.161 Z"
          id="path186" /><path
          d="m 176.344,12.648096 h 1.97163 V 7.3713451 c 0,-1.3180875 0.85159,-2.3567141 2.16527,-2.3567141 1.15966,0 1.71418,0.6073325 1.74718,2.0090383 v 5.6244267 h 1.97383 v -6.14374 c 0,-2.0068378 -1.22566,-3.0454643 -3.16869,-3.0454643 -1.17725,0 -2.19828,0.605132 -2.68018,1.4193096 h -0.0374 V 0.288 H 176.344 Z"
          id="path188" /><path
          d="m 83.467,30.528297 h 2.235688 l 1.159653,-3.274315 h 4.933476 l 1.159653,3.274315 h 2.319306 L 90.515137,18.166 h -2.301702 z m 5.851076,-10.232232 h 0.05501 l 1.850604,5.314159 h -3.773823 z"
          id="path190" /><path
          d="m 103.967,21.581727 h -1.97383 v 1.225668 h -0.0308 c -0.50611,-1.001219 -1.52713,-1.472121 -2.649375,-1.472121 -2.545956,0 -4.048883,2.077253 -4.048883,4.482377 0,2.56576 1.177256,4.713429 4.011475,4.713429 1.111243,0 2.127863,-0.587529 2.686783,-1.575544 h 0.0308 v 1.364297 c 0,1.476523 -0.70856,2.292901 -2.301703,2.292901 -1.003419,0 -1.901214,-0.198044 -2.145468,-1.315887 h -1.97383 c 0.171637,2.094857 2.20048,2.783607 4.000472,2.783607 2.818819,0 4.394359,-1.335692 4.394359,-4.020277 z m -4.376755,7.387012 c -1.645959,0 -2.354513,-1.489725 -2.354513,-2.957445 0,-1.487525 0.605132,-3.120281 2.354513,-3.120281 1.711975,0 2.402925,1.425911 2.402925,2.961846 0,1.527133 -0.65794,3.11588 -2.402925,3.11588"
          id="path192" /><path
          d="m 107.02,25.260456 c 0.0506,-1.333491 0.98582,-2.374318 2.35451,-2.374318 1.33349,0 2.18068,1.131047 2.24669,2.374318 z m 6.57503,1.296083 c 0.33008,-2.680185 -1.3995,-5.22614 -4.22052,-5.22614 -2.66698,0 -4.32834,2.178475 -4.32834,4.724431 0,2.755001 1.57554,4.711227 4.37895,4.711227 1.95623,0 3.61759,-1.089237 4.05109,-3.052065 h -1.87041 c -0.34548,0.992416 -1.03863,1.489724 -2.18068,1.489724 -1.64375,0 -2.40512,-1.243271 -2.40512,-2.647177 z"
          id="path194" /><path
          d="m 114.623,30.528605 h 1.97383 v -5.285553 c 0,-1.311486 0.84719,-2.354513 2.16307,-2.354513 1.15745,0 1.71418,0.609533 1.74718,2.01564 v 5.624426 h 1.97163 v -6.14594 c 0,-2.011239 -1.22346,-3.047665 -3.16429,-3.047665 -1.17945,0 -2.20048,0.602932 -2.79021,1.593148 l -0.0308,-0.03961 V 21.579253 H 114.623 Z"
          id="path196" /><path
          d="m 132.093,24.561552 c -0.19144,-2.196079 -1.95843,-3.234705 -4.03348,-3.234705 -2.94424,0 -4.41196,2.114661 -4.41196,4.81465 0,2.629574 1.53593,4.623209 4.34375,4.623209 2.3017,0 3.73641,-1.285081 4.10169,-3.599986 h -1.97383 c -0.19144,1.28068 -0.98582,2.035444 -2.12786,2.035444 -1.71418,0 -2.36992,-1.575543 -2.36992,-3.058667 0,-2.717593 1.43471,-3.258911 2.45573,-3.258911 1.09144,0 1.88802,0.589729 2.04205,1.678966 z"
          id="path198" /><path
          d="m 135.626,30.489162 -0.22225,0.69095 c -0.24425,0.770168 -0.4687,1.252073 -1.3841,1.252073 -0.31467,0 -0.62494,-0.07041 -0.9374,-0.125427 v 1.663563 c 0.45109,0.07262 0.89999,0.105623 1.36869,0.105623 2.05965,0 2.52836,-1.454517 3.16869,-3.063068 l 3.47676,-9.435658 h -2.06185 l -2.26429,6.674055 h -0.033 l -2.33691,-6.674055 h -2.16527 z"
          id="path200" /><path
          d="m 151.123,30.770658 c 2.87163,0 4.51759,-1.978231 4.51759,-4.726631 0,-2.737397 -1.64596,-4.709027 -4.51759,-4.709027 -2.87603,0 -4.51979,1.97163 -4.51979,4.709027 0,2.7484 1.64376,4.726631 4.51979,4.726631 m 0,-1.564541 c -1.76699,0 -2.54596,-1.60415 -2.54596,-3.16209 0,-1.540336 0.77897,-3.155488 2.54596,-3.155488 1.76699,0 2.54375,1.615152 2.54375,3.155488 0,1.55794 -0.77676,3.16209 -2.54375,3.16209"
          id="path202" /><path
          d="m 155.92,23.049233 h 1.47212 v 7.479432 h 1.97163 v -7.479432 h 1.68117 v -1.469921 h -1.68117 v -0.922001 c 0,-0.743762 0.4335,-0.935204 0.97261,-0.935204 0.39829,0 0.65575,0.03961 0.9132,0.103423 v -1.538136 c -0.30806,-0.08142 -0.75916,-0.118826 -1.3819,-0.118826 -1.28288,0 -2.47554,0.380684 -2.47554,2.666982 v 0.743762 H 155.92 Z"
          id="path204" /><path
          d="m 177.853,22.094016 c -0.25746,-2.66038 -2.46014,-4.198516 -5.24374,-4.220521 -3.70781,0 -5.9215,2.944243 -5.9215,6.471612 0,3.533971 2.21369,6.480414 5.9215,6.480414 2.99265,0 5.08751,-2.046447 5.25914,-5.008293 h -2.11026 c -0.17163,1.802193 -1.22786,3.234706 -3.14888,3.234706 -2.64938,0 -3.76062,-2.33471 -3.76062,-4.706827 0,-2.369917 1.11124,-4.704626 3.76062,-4.704626 1.79779,0 2.71759,1.038626 3.07847,2.453535 z"
          id="path206" /><path
          d="m 186.581,23.927675 c 0,-1.885811 -1.8352,-2.598767 -3.58238,-2.598767 -1.97603,0 -3.93226,0.677748 -4.07089,2.981651 h 1.97383 c 0.0902,-0.972613 0.86699,-1.425911 1.97383,-1.425911 0.79658,0 1.85281,0.193642 1.85281,1.219065 0,1.157453 -1.26088,0.999018 -2.68239,1.260875 -1.66356,0.189242 -3.44375,0.552321 -3.44375,2.790209 0,1.744981 1.45012,2.61197 3.06087,2.61197 1.05843,0 2.3193,-0.325671 3.10047,-1.089238 0.15404,0.809777 0.72836,1.089238 1.52274,1.089238 0.33227,0 0.9528,-0.118826 1.24547,-0.224449 v -1.370899 c -0.20685,0.03081 -0.36088,0.03081 -0.48411,0.03081 -0.36308,0 -0.4665,-0.187041 -0.4665,-0.673347 z m -1.97603,3.584582 c 0,1.243271 -1.34669,1.689969 -2.21368,1.689969 -0.69095,0 -1.8176,-0.253056 -1.8176,-1.131047 0,-1.043028 0.76357,-1.359897 1.61075,-1.491926 0.86259,-0.160635 1.8198,-0.14083 2.42053,-0.541318 z"
          id="path208" /><path
          d="m 188.23,30.528605 h 1.97383 v -5.285553 c 0,-1.311486 0.84719,-2.354513 2.16307,-2.354513 1.15745,0 1.71418,0.609533 1.74718,2.01564 v 5.624426 h 1.97603 v -6.14594 c 0,-2.011239 -1.23226,-3.047665 -3.16869,-3.047665 -1.17945,0 -2.19828,0.602932 -2.788,1.593148 l -0.033,-0.03961 V 21.579253 H 188.23 Z"
          id="path210" /><path
          d="m 205.183,23.927675 c 0,-1.885811 -1.8374,-2.598767 -3.58458,-2.598767 -1.97603,0 -3.93006,0.677748 -4.07089,2.981651 h 1.97383 c 0.088,-0.972613 0.86479,-1.425911 1.97163,-1.425911 0.79877,0 1.85501,0.193642 1.85501,1.219065 0,1.157453 -1.26528,0.999018 -2.68239,1.260875 -1.66136,0.189242 -3.44595,0.552321 -3.44595,2.790209 0,1.744981 1.45452,2.61197 3.06527,2.61197 1.05403,0 2.3193,-0.325671 3.10047,-1.089238 0.15404,0.809777 0.72616,1.089238 1.52274,1.089238 0.32787,0 0.9506,-0.118826 1.24547,-0.224449 v -1.370899 c -0.20905,0.03081 -0.36528,0.03081 -0.48631,0.03081 -0.36308,0 -0.4643,-0.187041 -0.4643,-0.673347 z m -1.97383,3.584582 c 0,1.243271 -1.3533,1.689969 -2.21808,1.689969 -0.69316,0 -1.8198,-0.253056 -1.8198,-1.131047 0,-1.043028 0.76357,-1.359897 1.61295,-1.491926 0.86479,-0.160635 1.8154,-0.14083 2.42493,-0.541318 z"
          id="path212" /><path
          d="m 215.257,18.159651 h -1.96943 v 4.565996 h -0.0374 c -0.60513,-0.981415 -1.8528,-1.399506 -2.97725,-1.399506 -1.95622,0 -3.87724,1.42151 -3.87724,4.656216 0,2.684586 1.3687,4.781643 4.18971,4.781643 1.12665,0 2.24889,-0.433495 2.7682,-1.456718 h 0.0352 v 1.214665 h 1.86821 z m -6.8875,7.981141 c 0,-1.612952 0.65574,-3.261112 2.51075,-3.261112 1.52273,0 2.47333,1.183858 2.47333,3.155488 0,1.560141 -0.74376,3.16209 -2.51074,3.16209 -1.71198,0 -2.47334,-1.518331 -2.47334,-3.056466"
          id="path214" /><path
          d="m 224.42,23.927675 c 0,-1.885811 -1.833,-2.598767 -3.58238,-2.598767 -1.97383,0 -3.93226,0.677748 -4.07089,2.981651 h 1.97383 c 0.0858,-0.972613 0.86919,-1.425911 1.97383,-1.425911 0.79658,0 1.85501,0.193642 1.85501,1.219065 0,1.157453 -1.26748,0.999018 -2.68679,1.260875 -1.66136,0.189242 -3.44595,0.552321 -3.44595,2.790209 0,1.744981 1.45672,2.61197 3.06747,2.61197 1.05403,0 2.3171,-0.325671 3.09607,-1.089238 0.15624,0.809777 0.72836,1.089238 1.52714,1.089238 0.32567,0 0.9506,-0.118826 1.24547,-0.224449 v -1.370899 c -0.20905,0.03081 -0.36528,0.03081 -0.48631,0.03081 -0.36088,0 -0.4665,-0.187041 -0.4665,-0.673347 z m -1.97603,3.584582 c 0,1.243271 -1.3489,1.689969 -2.21588,1.689969 -0.69096,0 -1.8176,-0.253056 -1.8176,-1.131047 0,-1.043028 0.76577,-1.359897 1.61075,-1.491926 0.86479,-0.160635 1.8198,-0.14083 2.42273,-0.541318 z"
          id="path216" /></g>

    </svg>
  )


}

export const Phacsignature = ({
  // Note: rbg values come from: canada.ca/en/treasury-board-secretariat/services/government-communications/design-standard/colour-design-standard-fip.html#toc1
  lang = 'en',
  textColor = 'black',
  variant = 'color',
  width = '20%',
}: PhacsignatureConfig) => {
  const canadaRed = '#EA2D37';
  const flagColor = (variant === 'color') ? canadaRed : textColor;
  if (lang === 'fr') {
    return <FrenchGovGouv textColor={textColor}  flagColor={canadaRed}/>
  } else {
    return <EnglishGovGouv textColor={textColor} flagColor={canadaRed}/>
  }

}