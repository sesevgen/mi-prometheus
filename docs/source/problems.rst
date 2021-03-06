.. role:: hidden
    :class: hidden-section

Problems
============

.. automodule:: miprometheus.problems
.. currentmodule:: miprometheus.problems

Base Problem
--------------

.. automodule:: miprometheus.problems.problem
    :members:
    :special-members:
    :exclude-members: __dict__,__weakref__

ProblemFactory
-----------------
.. currentmodule:: miprometheus.problems
.. autoclass:: ProblemFactory
    :members:
    :special-members:
    :exclude-members: __dict__,__weakref__

ImageTextToClass Problems
----------------------------

.. automodule:: miprometheus.problems.image_text_to_class.image_text_to_class_problem
    :members:
    :special-members:
    :exclude-members: __dict__,__weakref__

:hidden:`CLEVR`
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
.. automodule:: miprometheus.problems.image_text_to_class.clevr
    :members:
    :special-members:
    :exclude-members: __dict__,__weakref__

:hidden:`ShapeColorQuery`
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
.. automodule:: miprometheus.problems.image_text_to_class.shape_color_query
    :members:
    :special-members:
    :exclude-members: __dict__,__weakref__

:hidden:`Sort-Of-CLEVR`
~~~~~~~~~~~~~~~~~~~~~~~~
.. automodule:: miprometheus.problems.image_text_to_class.sort_of_clevr
    :members:
    :special-members:
    :exclude-members: __dict__,__weakref__

ImageToClass Problems
----------------------------

.. automodule:: miprometheus.problems.image_to_class.image_to_class_problem
    :members:
    :special-members:
    :exclude-members: __dict__,__weakref__

:hidden:`CIFAR-10`
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
.. automodule:: miprometheus.problems.image_to_class.cifar10
    :members:
    :special-members:
    :exclude-members: __dict__,__weakref__

:hidden:`MNIST`
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
.. automodule:: miprometheus.problems.image_to_class.mnist
    :members:
    :special-members:
    :exclude-members: __dict__,__weakref__

SequenceToSequence Problems
----------------------------

.. automodule:: miprometheus.problems.seq_to_seq.seq_to_seq_problem
    :members:
    :special-members:
    :exclude-members: __dict__,__weakref__

Algorithmic SequenceToSequence Problems
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
.. automodule:: miprometheus.problems.seq_to_seq.algorithmic.algorithmic_seq_to_seq_problem
    :members:
    :special-members:
    :exclude-members: __dict__,__weakref__

:hidden:`Dual Comparison`
`````````````````````````````
.. automodule:: miprometheus.problems.seq_to_seq.algorithmic.dual_comparison.sequence_comparison_cl
    :members:
    :special-members:
    :exclude-members: __dict__,__weakref__

.. automodule:: miprometheus.problems.seq_to_seq.algorithmic.dual_comparison.sequence_equality_cl
    :members:
    :special-members:
    :exclude-members: __dict__,__weakref__

.. automodule:: miprometheus.problems.seq_to_seq.algorithmic.dual_comparison.sequence_symmetry_cl
    :members:
    :special-members:
    :exclude-members: __dict__,__weakref__

:hidden:`Dual Distraction`
`````````````````````````````
.. automodule:: miprometheus.problems.seq_to_seq.algorithmic.dual_distraction.distraction_carry
    :members:
    :special-members:
    :exclude-members: __dict__,__weakref__

.. automodule:: miprometheus.problems.seq_to_seq.algorithmic.dual_distraction.distraction_forget
    :members:
    :special-members:
    :exclude-members: __dict__,__weakref__

.. automodule:: miprometheus.problems.seq_to_seq.algorithmic.dual_distraction.distraction_ignore
    :members:
    :special-members:
    :exclude-members: __dict__,__weakref__

:hidden:`Dual Ignore`
`````````````````````````````
.. automodule:: miprometheus.problems.seq_to_seq.algorithmic.dual_ignore.interruption_not
    :members:
    :special-members:
    :exclude-members: __dict__,__weakref__

.. automodule:: miprometheus.problems.seq_to_seq.algorithmic.dual_ignore.interruption_reverse_recall
    :members:
    :special-members:
    :exclude-members: __dict__,__weakref__

.. automodule:: miprometheus.problems.seq_to_seq.algorithmic.dual_ignore.interruption_swap_recall
    :members:
    :special-members:
    :exclude-members: __dict__,__weakref__

:hidden:`Manipulation Spatial`
`````````````````````````````````
.. automodule:: miprometheus.problems.seq_to_seq.algorithmic.manipulation_spatial.manipulation_spatial_not
    :members:
    :special-members:
    :exclude-members: __dict__,__weakref__

.. automodule:: miprometheus.problems.seq_to_seq.algorithmic.manipulation_spatial.manipulation_spatial_rotation
    :members:
    :special-members:
    :exclude-members: __dict__,__weakref__

:hidden:`Manipulation Temporal`
`````````````````````````````````
.. automodule:: miprometheus.problems.seq_to_seq.algorithmic.manipulation_temporal.manipulation_temporal_swap
    :members:
    :special-members:
    :exclude-members: __dict__,__weakref__

.. automodule:: miprometheus.problems.seq_to_seq.algorithmic.manipulation_temporal.skip_recall_cl
    :members:
    :special-members:
    :exclude-members: __dict__,__weakref__

:hidden:`Recall`
`````````````````````````````
.. automodule:: miprometheus.problems.seq_to_seq.algorithmic.recall.operation_span
    :members:
    :special-members:
    :exclude-members: __dict__,__weakref__

.. automodule:: miprometheus.problems.seq_to_seq.algorithmic.recall.reading_span
    :members:
    :special-members:
    :exclude-members: __dict__,__weakref__

.. automodule:: miprometheus.problems.seq_to_seq.algorithmic.recall.repeat_reverse_recall_cl
    :members:
    :special-members:
    :exclude-members: __dict__,__weakref__

.. automodule:: miprometheus.problems.seq_to_seq.algorithmic.recall.repeat_serial_recall_cl
    :members:
    :special-members:
    :exclude-members: __dict__,__weakref__

.. automodule:: miprometheus.problems.seq_to_seq.algorithmic.recall.reverse_recall_cl
    :members:
    :special-members:
    :exclude-members: __dict__,__weakref__

.. automodule:: miprometheus.problems.seq_to_seq.algorithmic.recall.scratch_pad_cl
    :members:
    :special-members:
    :exclude-members: __dict__,__weakref__

.. automodule:: miprometheus.problems.seq_to_seq.algorithmic.recall.serial_recall_cl
    :members:
    :special-members:
    :exclude-members: __dict__,__weakref__


TextToText Problems
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
.. automodule:: miprometheus.problems.seq_to_seq.text2text.text_to_text_problem
    :members:
    :special-members:
    :exclude-members: __dict__,__weakref__

:hidden:`Translation`
`````````````````````````````
.. automodule:: miprometheus.problems.seq_to_seq.text2text.translation_anki
    :members:
    :special-members:
    :exclude-members: __dict__,__weakref__


VideoToClass Problems
----------------------------

.. automodule:: miprometheus.problems.video_to_class.video_to_class_problem
    :members:
    :special-members:
    :exclude-members: __dict__,__weakref__

:hidden:`Sequential MNIST`
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
.. automodule:: miprometheus.problems.video_to_class.seq_mnist_to_class.permuted_sequential_row_mnist
    :members:
    :special-members:
    :exclude-members: __dict__,__weakref__

.. automodule:: miprometheus.problems.video_to_class.seq_mnist_to_class.sequential_pixel_mnist
    :members:
    :special-members:
    :exclude-members: __dict__,__weakref__
