
if [ "$#" -ne 2 ]; then
  echo "${0##*/}: error: exactly two input arguments must be given";
  echo "usage: ${0##*/} {CONCEPT_LISTS_FILE} {RESULTS_FILE}";
  exit 1;
fi

### check that results file has the expected number of results ###
NLST=$(awk '{print $1}' $1 | wc -w);
NRES=$(awk '{print $1}' $2 | wc -w);
if [ "$NLST" != "$NRES" ]; then
  echo "${0##*/}: error: $2 has $NRES results and expected the same as $1 which has $NLST lines";
  exit 1;
fi

awk -v clst=$1 -v ecode=0 '
  {
    ### load concept list for the n-th image ###
    getline line < clst;
    NL=split(line,lst," ");

    ### check that concept list and result corresponds to same ID ###
    if( lst[1] != $1 ) {
      printf("error: unexpected order of results, line %d image ID mismatch %s != %s\n",NR,$1,lst[1]);
      exit 1;
    }

    ### check that result line has the expected number of fields ###
    if( (NL-1) != ((NF-1)/2) ) {
      printf("error: unexpected number of fields (%d, and should be %d) for line %d\n",NF,1+2*(NL-1),NR);
      ecode=1;
      next;
    }

    ### check that scores are numeric ###
    for(n=2;n<=NF;n+=2)
      if( ! ( $n == 0+$n ) ) {
        printf("error: unexpected result format, line %d field %d (concept score) should be a number, it is %s\n",NR,n,$n);
        ecode=1;
        next;
      }

    ### check that decisions are either 0 or 1 ###
    for(n=3;n<=NF;n+=2)
      if( ! ($n==0 || $n==1) ) {
        printf("error: unexpected result format, line %d field %d (concept decision) should be either 0 or 1, it is %s\n",NR,n,$n);
        ecode=1;
        next;
      }

  }
  END {
    exit ecode;
  }
  ' $2;

exit $?;