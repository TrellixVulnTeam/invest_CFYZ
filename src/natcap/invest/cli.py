# TODO: make logging level global and you mentioned that you were thinking of adding a dropbdown box.

# coding=UTF-8
"""Single entry point for all InVEST applications."""
from __future__ import absolute_import

import argparse
import os
import importlib
import logging
import sys
import collections
import pprint
import warnings  # TODO: unused import
import multiprocessing

try:
    from . import utils
except ValueError:
    # When we're in a pyinstaller build, this isn't a module.
    from natcap.invest import utils

import six # TODO: should this go above the utils import for PEP8 standards, or does it have to go last?

LOGGER = logging.getLogger(__name__)
_UIMETA = collections.namedtuple('UIMeta', 'pyname gui aliases')

_MODEL_UIS = {
    'carbon': _UIMETA(
        pyname='natcap.invest.carbon',
        gui='carbon.Carbon',
        aliases=()),
    'coastal_blue_carbon': _UIMETA(
        pyname='natcap.invest.coastal_blue_carbon.coastal_blue_carbon',
        gui='cbc.CoastalBlueCarbon',
        aliases=('cbc',)),
    'coastal_blue_carbon_preprocessor': _UIMETA(
        pyname='natcap.invest.coastal_blue_carbon.preprocessor',
        gui='cbc.CoastalBlueCarbonPreprocessor',
        aliases=('cbc_pre',)),
    'coastal_vulnerability': _UIMETA(
        pyname='natcap.invest.coastal_vulnerability.coastal_vulnerability',
        gui='cv.CoastalVulnerability',
        aliases=('cv',)),
    'crop_production_percentile': _UIMETA(
        pyname='natcap.invest.crop_production_percentile',
        gui='crop_production.CropProductionPercentile',
        aliases=('cpp',)),
    'crop_production_regression': _UIMETA(
        pyname='natcap.invest.crop_production_regression',
        gui='crop_production.CropProductionRegression',
        aliases=('cpr',)),
    'delineateit': _UIMETA(
        pyname='natcap.invest.routing.delineateit',
        gui='routing.Delineateit',
        aliases=()),
    'finfish_aquaculture': _UIMETA(
        pyname='natcap.invest.finfish_aquaculture.finfish_aquaculture',
        gui='finfish.FinfishAquaculture',
        aliases=()),
    'fisheries': _UIMETA(
        pyname='natcap.invest.fisheries.fisheries',
        gui='fisheries.Fisheries',
        aliases=()),
    'fisheries_hst': _UIMETA(
        pyname='natcap.invest.fisheries.fisheries_hst',
        gui='fisheries.FisheriesHST',
        aliases=()),
    'forest_carbon_edge_effect': _UIMETA(
        pyname='natcap.invest.forest_carbon_edge_effect',
        gui='forest_carbon.ForestCarbonEdgeEffect',
        aliases=('fc',)),
    'globio': _UIMETA(
        pyname='natcap.invest.globio',
        gui='globio.GLOBIO',
        aliases=()),
    'habitat_quality': _UIMETA(
        pyname='natcap.invest.habitat_quality',
        gui='habitat_quality.HabitatQuality',
        aliases=('hq',)),
    'habitat_risk_assessment': _UIMETA(
        pyname='natcap.invest.habitat_risk_assessment.hra',
        gui='hra.HabitatRiskAssessment',
        aliases=('hra',)),
    'habitat_risk_assessment_preprocessor': _UIMETA(
        pyname='natcap.invest.habitat_risk_assessment.hra_preprocessor',
        gui='hra.HRAPreprocessor',
        aliases=('hra_pre',)),
    'hydropower_water_yield': _UIMETA(
        pyname='natcap.invest.hydropower.hydropower_water_yield',
        gui='hydropower.HydropowerWaterYield',
        aliases=('hwy',)),
    'ndr': _UIMETA(
        pyname='natcap.invest.ndr.ndr',
        gui='ndr.Nutrient',
        aliases=()),
    'overlap_analysis': _UIMETA(
        pyname='natcap.invest.overlap_analysis.overlap_analysis',
        gui='overlap_analysis.OverlapAnalysis',
        aliases=('oa',)),
    'overlap_analysis_mz': _UIMETA(
        pyname='natcap.invest.overlap_analysis.overlap_analysis_mz',
        gui='overlap_analysis.OverlapAnalysisMZ',
        aliases=('oa_mz',)),
    'pollination': _UIMETA(
        pyname='natcap.invest.pollination',
        gui='pollination.Pollination',
        aliases=()),
    'recreation': _UIMETA(
        pyname='natcap.invest.recreation.recmodel_client',
        gui='recreation.Recreation',
        aliases=()),
    'routedem': _UIMETA(
        pyname='natcap.invest.routing.routedem',
        gui='routing.RouteDEM',
        aliases=()),
    'scenario_generator': _UIMETA(
        pyname='natcap.invest.scenario_generator.scenario_generator',
        gui='scenario_gen.ScenarioGenerator',
        aliases=('sg',)),
    'scenario_generator_proximity': _UIMETA(
        pyname='natcap.invest.scenario_gen_proximity',
        gui='scenario_gen.ScenarioGenProximity',
        aliases=('sgp',)),
    'scenic_quality': _UIMETA(
        pyname='natcap.invest.scenic_quality.scenic_quality',
        gui='scenic_quality.ScenicQuality',
        aliases=('sq',)),
    'sdr': _UIMETA(
        pyname='natcap.invest.sdr',
        gui='sdr.SDR',
        aliases=()),
    'seasonal_water_yield': _UIMETA(
        pyname='natcap.invest.seasonal_water_yield.seasonal_water_yield',
        gui='seasonal_water_yield.SeasonalWaterYield',
        aliases=('swy',)),
    'wind_energy': _UIMETA(
        pyname='natcap.invest.wind_energy.wind_energy',
        gui='wind_energy.WindEnergy',
        aliases=()),
    'wave_energy': _UIMETA(
        pyname='natcap.invest.wave_energy.wave_energy',
        gui='wave_energy.WaveEnergy',
        aliases=()),
    'habitat_suitability': _UIMETA(
        pyname='natcap.invest.habitat_suitability',
        gui=None,
        aliases=('hs',)),
}


def _format_args(args_dict):  # TODO: worth a docstring?
    sorted_args = sorted(six.iteritems(args_dict), key=lambda x: x[0])

    max_key_width = 0
    if len(sorted_args) > 0:
        max_key_width = max(len(x[0]) for x in sorted_args)

    format_str = u"%-" + six.text_type(str(max_key_width)) + u"s %s"

    args_string = u'\n'.join([format_str % (arg) for arg in sorted_args])
    args_string = u"Arguments:\n%s\n" % args_string
    return args_string


def _import_ui_class(gui_class): # TODO: worth a docstring?
    mod_name, classname = gui_class.split('.')
    module = importlib.import_module(
        name='.ui.%s' % mod_name,
        package='natcap.invest')
    return getattr(module, classname)

# metadata for models: full modelname, first released, full citation,
# local documentation name.


# Goal: allow InVEST models to be run at the command-line, without a UI.
#   problem: how to identify which models have Qt UIs available?
#       1.  If we can't import the ui infrastructure, we don't have any qt uis.
#       2.  We could iterate through all the model UI files and Identify the
#           model from its name and attributes.
#       3.  We could access a pre-processed list of models available, perhaps
#           written to a file during the setuptools build step.
#   problem: how to identify which models are available to the API?
#       1.  Recursively import natcap.invest and look for modules with execute
#           functions available.
#       2.  Import all of the execute functions to a known place (an __init__
#           file?).
#   problem: how to provide parameters?
#       1.  If execute is parseable, just extract parameters from the docstring
#           and allow each param to be provided as a CLI flag.
#       2.  Allow parameters to be passed as a JSON file
#       3.  Allow model to run with a scenario file.
#       PS: Optionally, don't validate inputs, but do validate by default.


def list_models():  # TODO: worth a docstring, or consider whether you want this to be a function at all?  returning sorted(_MODEL_UIS.keys()) would be fine w/ me if it were inline
    return sorted(_MODEL_UIS.keys())


def format_models(): # TODO: maybe literally call it pretty_print_models?
    """Pretty-print available models."""
    print 'Available models:'
    model_names = list_models()
    max_model_name_length = max(len(name) for name in model_names)
    max_alias_name_length = max(len(', '.join(meta.aliases))
                                for meta in _MODEL_UIS.values())
    template_string = '    {modelname} {aliases}   {usage}'
    strings = []
    for model_name in list_models():
        usage_string = '(No GUI available)'
        if _MODEL_UIS[model_name].gui is not None:
            usage_string = ''

        alias_string = ', '.join(_MODEL_UIS[model_name].aliases)
        if alias_string:
            alias_string = '(%s)' % alias_string

        strings.append(template_string.format(
            modelname=model_name.ljust(max_model_name_length),
            aliases=alias_string.ljust(max_alias_name_length),
            usage=usage_string))
    return strings


class ListModelsAction(argparse.Action):  # TODO: docstring for this class
    def __init__(self,
                 option_strings,
                 dest,
                 default=False,
                 required=False,
                 help=None, *args, **kwargs):
        super(ListModelsAction, self).__init__(
            option_strings=option_strings,
            dest=dest,
            const=True,
            nargs=0,
            default=default,
            required=required,
            help=help, *args, **kwargs)

    def __call__(self, parser, namespace, values, option_string): # TODO: FYI, this marks as different function signature than overridden call, because `option_string` is optional i.e. `option_string=None`.  And maybe worth a short docstring?
        setattr(namespace, self.dest, self.const)
        parser.exit(message='\n'.join(format_models()) + '\n')


class SelectModelAction(argparse.Action):  # TODO: worth a docstring?
    def __call__(self, parser, namespace, values, option_string):  # TODO: same as above w/ option_string=None + docstring
        if values in ['', None]:
            parser.print_help()
            print '\n'.join(format_models())
            parser.exit()
        else:
            known_models = list_models()

            # map {alias: model}
            known_aliases = {}
            for modelname, meta in _MODEL_UIS.iteritems():
                for alias in meta.aliases:
                    assert alias not in known_aliases, (  # TODO: could there be a better place to check for this?  If an alias is repeated, it means we won't discover until a user tries to run a model on the command line.  If it's important and you expect it to be a common issue, maybe put it globally right after the dictionary is defined?
                        'Alias %s already defined for model %s') % (
                            alias, known_aliases[alias])
                    known_aliases[alias] = modelname

            matching_models = [model for model in known_models if
                               model.startswith(values)]

            exact_matches = [model for model in known_models if
                             model == values]

            if len(matching_models) == 1:  # match an identifying substring
                modelname = matching_models[0]
            elif len(exact_matches) == 1:  # match an exact modelname
                modelname = exact_matches[0]
            elif values in known_aliases:  # match an alias
                modelname = known_aliases[values]
            elif len(matching_models) == 0:
                parser.exit("Error: '%s' not a known model" % values)
            else:
                parser.exit((
                    "Model string '{model}' is ambiguous:\n"
                    "    {matching_models}").format(
                        model=values,
                        matching_models=' '.join(matching_models)))
        setattr(namespace, self.dest, modelname)


def write_console_files(out_dir, extension):  # TODO: where is this used?  I couldn't find anything with a grep.
    """
    Write out console files for each of the target models to the output dir.

    Parameters:
        out_dir: The directory in which to save the console files.
        extension: The extension of the output files (e.g. 'bat', 'sh')

    Returns:
        Nothing.  Writes files to out_dir, though.
    """
    content_template = "invest %(model)s\n"
    filename_template = os.path.join(out_dir, "invest_%(modelname)s_.%(ext)s")
    for model_name in list_models():
        console_filepath = filename_template % {
            'modelname': model_name, 'ext': extension}
        console_file = open(console_filepath)
        console_file.write(content_template % {'model': model_name})
        console_file.close()


def main():
    """
    Single entry point for all InVEST model user interfaces.

    This function provides a CLI for calling InVEST models, though it it very
    primitive.  Apart from displaying a help message and the version, this
    function will also (optionally) list the known models (based on the found
    json filenames) and will fire up an IUI interface based on the model name  # TODO: no longer based on json filenames, right?
    provided.
    """

    parser = argparse.ArgumentParser(description=(
        'Integrated Valuation of Ecosystem Services and Tradeoffs.  '
        'InVEST (Integrated Valuation of Ecosystem Services and Tradeoffs) is '
        'a family of tools for quantifying the values of natural capital in '
        'clear, credible, and practical ways. In promising a return (of '
        'societal benefits) on investments in nature, the scientific community '
        'needs to deliver knowledge and tools to quantify and forecast this '
        'return. InVEST enables decision-makers to quantify the importance of '
        'natural capital, to assess the tradeoffs associated with alternative '
        'choices, and to integrate conservation and human development.  \n\n'
        'Older versions of InVEST ran as script tools in the ArcGIS ArcToolBox '
        'environment, but have almost all been ported over to a purely '
        'open-source python environment.'),
        prog='invest'
    )
    list_group = parser.add_mutually_exclusive_group()
    verbosity_group = parser.add_mutually_exclusive_group()
    import natcap.invest

    parser.add_argument('--version', action='version',
                        version=natcap.invest.__version__)
    verbosity_group.add_argument('-v', '--verbose', dest='verbosity', default=0,
                                 action='count', help=('Increase verbosity'))
    verbosity_group.add_argument('--debug', dest='log_level',
                                 default=logging.CRITICAL,
                                 action='store_const', const=logging.DEBUG,
                                 help='Enable debug logging. Alias for -vvvvv')
    list_group.add_argument('--list', action=ListModelsAction,
                            help='List available models')
    parser.add_argument('-l', '--headless', action='store_true', dest='headless',
                        help=('Attempt to run InVEST without its GUI.'))
    parser.add_argument('-s', '--scenario', default=None, nargs='?',
                        help='Run the specified model with this scenario')
    parser.add_argument('-w', '--workspace', default=None, nargs='?',
                        help='The workspace in which outputs will be saved')

    gui_options_group = parser.add_argument_group(
        'gui options', 'These options are ignored if running in headless mode')
    gui_options_group.add_argument('-q', '--quickrun', action='store_true',
                                   help=('Run the target model without '
                                         'validating and quit with a nonzero '
                                         'exit status if an exception is '
                                         'encountered'))

    cli_options_group = parser.add_argument_group('headless options')
    cli_options_group.add_argument('-y', '--overwrite', action='store_true',
                                   default=False,
                                   help=('Overwrite the workspace without '
                                         'prompting for confirmation'))
    cli_options_group.add_argument('-n', '--no-validate', action='store_true',
                                   dest='validate', default=True,
                                   help=('Do not validate inputs before '
                                         'running the model.'))

    list_group.add_argument('model', action=SelectModelAction, nargs='?',
                            help=('The model/tool to run. Use --list to show '
                                  'available models/tools. Identifiable model '
                                  'prefixes may also be used.'))

    args = parser.parse_args()

    root_logger = logging.getLogger()
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter(
        fmt='%(asctime)s %(name)-18s %(levelname)-8s %(message)s',
        datefmt='%m/%d/%Y %H:%M:%S ')
    handler.setFormatter(formatter)

    # Set the log level based on what the user provides in the available
    # arguments.  Verbosity: the more v's the lower the logging threshold.
    # If --debug is used, the logging threshold is 10.
    # If the user goes lower than logging.DEBUG, default to logging.DEBUG.
    log_level = min(args.log_level, logging.CRITICAL - (args.verbosity*10))
    handler.setLevel(max(log_level, logging.DEBUG))  # don't go lower than DEBUG
    root_logger.addHandler(handler)
    LOGGER.info('Setting handler log level to %s', log_level)

    # FYI: Root logger by default has a level of logging.WARNING.
    # To capture ALL logging produced in this system at runtime, use this:
    # logging.getLogger().setLevel(logging.DEBUG)
    # Also FYI: using logging.DEBUG means that the logger will defer to
    # the setting of the parent logger.
    logging.getLogger('natcap').setLevel(logging.DEBUG)

    # Now that we've set up logging based on args, we can start logging.
    LOGGER.debug(args)

    try:
        # Importing model UI files here will usually import qtpy before we can
        # set the sip API in natcap.invest.ui.inputs.
        # Set it here, before we can do the actual importing.
        import sip
        sip.setapi('QString', 2)  # TODO: comment on what 2 is?

        from natcap.invest.ui import inputs
    except ImportError:
        print ('Error: ui not installed:\n'
               '    pip install natcap.invest[ui]')
        return 3  # TODO: comment on what 3 is?

    if args.headless:
        from natcap.invest import scenarios
        target_mod = _MODEL_UIS[args.model].pyname
        model_module = importlib.import_module(name=target_mod)
        LOGGER.info('imported target %s from %s',
                    model_module.__name__, model_module)

        paramset = scenarios.read_parameter_set(args.scenario)

        # prefer CLI option for workspace dir, but use paramset workspace if
        # the CLI options do not define a workspace.
        if args.workspace:
            workspace = os.path.abspath(args.workspace)
            paramset.args['workspace_dir'] = workspace
        else:
            if 'workspace_dir' in paramset.args:
                workspace = paramset.args['workspace_dir']
            else:
                parser.exit(3, (  # TODO: comment on 3, or if it's a special exit code then maybe a _GLOBAL?
                    'Workspace not defined. \n'
                    'Use --workspace to specify or add a '
                    '"workspace_dir" parameter to your scenario.'))

        with utils.prepare_workspace(workspace,
                                     name=paramset.name):
            LOGGER.info(_format_args(paramset.args))
            if not args.validate:
                LOGGER.info('Skipping validation by user request')
            else:
                model_warnings = []
                try:
                    model_warnings = getattr(
                        target_mod, 'validate')(paramset.args)
                except AttributeError:
                    LOGGER.warn(
                        '%s does not have a defined validation function.',
                        paramset.name)
                finally:
                    if model_warnings:
                        LOGGER.warn('Warnings found: \n%s',
                                    pprint.pformat(model_warnings))

            if not args.workspace:
                args.workspace = os.getcwd()

            # If the workspace exists and we don't have up-front permission to
            # overwrite the workspace, prompt for permission.
            if (os.path.exists(args.workspace) and
                    len(os.listdir(args.workspace)) > 0 and
                    not args.overwrite):
                overwrite_denied = False
                if not sys.stdout.isatty():
                    overwrite_denied = True
                else:
                    user_response = raw_input(
                        'Workspace exists: %s\n    Overwrite? (y/n) ' % (
                            os.path.abspath(args.workspace)))
                    while user_response not in ('y', 'n'):
                        user_response = raw_input(
                            "Response must be either 'y' or 'n': ")
                    if user_response == 'n':
                        overwrite_denied = True

                if overwrite_denied:
                    # Exit the parser with an error message.
                    parser.exit(2, ('Use --workspace to define an '  # TODO: comment on exit code
                                    'alternate workspace.  Aborting.'))
                else:
                    LOGGER.warning(
                        'Overwriting the workspace per user input %s',
                        os.path.abspath(args.workspace))

            if 'workspace_dir' not in paramset.args:
                paramset.args['workspace_dir'] = args.workspace

            getattr(model_module, 'execute')(paramset.args)
    else:
        model_classname = _import_ui_class(_MODEL_UIS[args.model].gui)
        model_form = model_classname()

        try:
            if args.scenario:
                model_form.load_scenario(args.scenario)
        except Exception as error:
            parser.exit('Could not load scenario: %s\n', error)  # TODO: should you raise the exception here too rather than try to run w/o a scenario?

        if args.workspace:
            model_form.workspace.set_value(args.workspace)

        model_form.run(quickrun=args.quickrun)
        app_exitcode = inputs.QT_APP.exec_()

        if model_form.form.run_dialog.messageArea.error:
            parser.exit(1, 'Model %s: run failed\n' % args.model)

        if app_exitcode != 0:
            parser.exit(app_exitcode,
                        'App terminated with exit code %s\n' % app_exitcode)

if __name__ == '__main__':
    multiprocessing.freeze_support()
    main()