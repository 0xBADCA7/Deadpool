import deadpool_dfa
import phoenixAES

def AesGetAllRoundKeys(targetbin, targetdata, goldendata,
        iblock=0x74657374746573747465737474657374,
        processinput=deadpool_dfa.processinput,
        processoutput=deadpool_dfa.processoutput,
        verbose=1,
        maxleaf=256*256,
        minleaf=64,
        minleafnail=8,
        addresses=None,
        start_from_left=True,
        depth_first_traversal=False,
        faults=4,
        minfaultspercol=4,
        timeoutfactor=2,
        savetraces_format='default',
        logfile=None,
        tolerate_error=False,
        lastroundkeys=[],
        encrypt=None,
        outputbeforelastrounds=False,
        shell=False,
        debug=False):

    foundkey=True
    while foundkey:
        foundkey=False
        engine=deadpool_dfa.Acquisition(
            targetbin, targetdata, goldendata, phoenixAES,
            iblock, processinput, processoutput,
            verbose, maxleaf, minleaf, minleafnail,
            addresses, start_from_left, depth_first_traversal,
            faults, minfaultspercol, timeoutfactor,
            savetraces_format, logfile,
            tolerate_error, lastroundkeys, encrypt,
            outputbeforelastrounds, shell, debug)
        tracefiles_sets=engine.run()

        if encrypt is not None:
            tracefiles = tracefiles_sets[not encrypt]
        else:
            assert len(tracefiles_sets[0])>0 or len(tracefiles_sets[1])>0
            if len(tracefiles_sets[0])>0:
                encrypt=True
                tracefiles=tracefiles_sets[0]
            elif len(tracefiles_sets[1])>0:
                encrypt=False
                tracefiles=tracefiles_sets[1]
            else:
                tracefiles=[]
        for tracefile in tracefiles:
            k=phoenixAES.crack(tracefile, lastroundkeys, encrypt, outputbeforelastrounds and len(lastroundkeys)>0, verbose)
            if k:
                foundkey=True
                lastroundkeys.append(k)
                open('lastroundkeys.log', 'w').write('\n'.join(lastroundkeys))
                break
    return lastroundkeys
