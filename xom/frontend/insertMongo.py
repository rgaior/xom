import os
import pymongo


client = pymongo.MongoClient()
db = client.testshanta  #change to client.(NameOfDatabase)
collection = db.inventory #change to db.(NameOfCollection)

entriesJson = [
    {"charge_yield": {"pvalue": 0, "chi2": 0, "names": ["charge_yield"], "values": 174.8370638645307, "errors": 1.1642972196361179, "run_number": 6841, "ndof": 0, "time": "2017-02-06 13:55:15"}},
    {"charge_yield": {"pvalue": 0, "chi2": 0, "names": ["charge_yield"], "values": 174.65102329053335, "errors": 0.5223795066168616, "run_number": 6842, "ndof": 0, "time": "2017-02-06 14:55:25"}},
    {"charge_yield": {"pvalue": 0, "chi2": 0, "names": ["charge_yield"], "values": 173.883664018734, "errors": 0.8705018210432067, "run_number": 6843, "ndof": 0, "time": "2017-02-06 15:55:35"}},
    {"charge_yield": {"pvalue": 0, "chi2": 0, "names": ["charge_yield"], "values": 173.34325419243962, "errors": 0.4534430994308614, "run_number": 6844, "ndof": 0, "time": "2017-02-06 16:55:59"}},
    {"charge_yield": {"pvalue": 0, "chi2": 0, "names": ["charge_yield"], "values": 174.04398745379828, "errors": 0.8738199710949057, "run_number": 6845, "ndof": 0, "time": "2017-02-06 17:56:10"}},
    {"charge_yield": {"pvalue": 0, "chi2": 0, "names": ["charge_yield"], "values": -4957.842558869735, "errors": 51.727541224979774, "run_number": 6848, "ndof": 0, "time": "2017-02-06 18:49:22"}},
    {"charge_yield": {"pvalue": 0, "chi2": 0, "names": ["charge_yield"], "values": 174.75383302795814, "errors": 0.7099940745773312, "run_number": 6849, "ndof": 0, "time": "2017-02-06 19:49:33"}},
    {"charge_yield": {"pvalue": 0, "chi2": 0, "names": ["charge_yield"], "values": 174.79428624017416, "errors": 0.7314121442828817, "run_number": 6850, "ndof": 0, "time": "2017-02-06 20:49:44"}},
    {"charge_yield": {"pvalue": 0, "chi2": 0, "names": ["charge_yield"], "values": 174.97358761732232, "errors": 0.7112434617477299, "run_number": 6851, "ndof": 0, "time": "2017-02-06 21:49:55"}},
    {"charge_yield": {"pvalue": 0, "chi2": 0, "names": ["charge_yield"], "values": 175.16169382722887, "errors": 0.4697635036100574, "run_number": 6852, "ndof": 0, "time": "2017-02-06 22:50:06"}},
    {"charge_yield": {"pvalue": 0, "chi2": 0, "names": ["charge_yield"], "values": 174.27959109633503, "errors": 0.8246479429540381, "run_number": 6853, "ndof": 0, "time": "2017-02-06 23:50:17"}},
    {"charge_yield": {"pvalue": 0, "chi2": 0, "names": ["charge_yield"], "values": 174.28676615565, "errors": 0.7862189681677736, "run_number": 6855, "ndof": 0, "time": "2017-02-07 01:50:43"}},
    {"charge_yield": {"pvalue": 0, "chi2": 0, "names": ["charge_yield"], "values": 173.2187510327681, "errors": 0.8068293944107134, "run_number": 6856, "ndof": 0, "time": "2017-02-07 02:50:53"}},
    {"charge_yield": {"pvalue": 0, "chi2": 0, "names": ["charge_yield"], "values": 173.81174189879354, "errors": 0.7453514287108288, "run_number": 6857, "ndof": 0, "time": "2017-02-07 03:51:04"}},
    {"charge_yield": {"pvalue": 0, "chi2": 0, "names": ["charge_yield"], "values": 174.4268924836659, "errors": 0.4482869774618576, "run_number": 6858, "ndof": 0, "time": "2017-02-07 04:51:15"}},
    {"charge_yield": {"pvalue": 0, "chi2": 0, "names": ["charge_yield"], "values": 173.53427440632802, "errors": 0.8787409898619418, "run_number": 6859, "ndof": 0, "time": "2017-02-07 05:51:27"}},
    {"charge_yield": {"pvalue": 0, "chi2": 0, "names": ["charge_yield"], "values": 174.05967200115987, "errors": 0.45229075852324907, "run_number": 6860, "ndof": 0, "time": "2017-02-07 06:51:38"}},
    {"charge_yield": {"pvalue": 0, "chi2": 0, "names": ["charge_yield"], "values": 173.6435635171164, "errors": 0.7210094465632803, "run_number": 6862, "ndof": 0, "time": "2017-02-07 08:52:05"}},
    {"charge_yield": {"pvalue": 0, "chi2": 0, "names": ["charge_yield"], "values": 314.7844312837897, "errors": 0.3828378692517573, "run_number": 6871, "ndof": 0, "time": "2017-02-07 18:36:03"}},
    {"charge_yield": {"pvalue": 0, "chi2": 0, "names": ["charge_yield"], "values": 174.23126430273453, "errors": 0.8254333552964953, "run_number": 6872, "ndof": 0, "time": "2017-02-07 19:36:15"}},
    {"charge_yield": {"pvalue": 0, "chi2": 0, "names": ["charge_yield"], "values": -3923.7225854801454, "errors": 0.44181923846386606, "run_number": 6873, "ndof": 0, "time": "2017-02-07 20:36:25"}},
    {"charge_yield": {"pvalue": 0, "chi2": 0, "names": ["charge_yield"], "values": 174.41305612000107, "errors": 1.207892560914169, "run_number": 6874, "ndof": 0, "time": "2017-02-07 21:36:36"}},
    {"charge_yield": {"pvalue": 0, "chi2": 0, "names": ["charge_yield"], "values": 174.55974710942837, "errors": 1.3570762168741737, "run_number": 6875, "ndof": 0, "time": "2017-02-07 22:36:47"}},
    {"charge_yield": {"pvalue": 0, "chi2": 0, "names": ["charge_yield"], "values": 173.8793256056413, "errors": 1.1922221253292908, "run_number": 6876, "ndof": 0, "time": "2017-02-07 23:36:58"}},
    {"charge_yield": {"pvalue": 0, "chi2": 0, "names": ["charge_yield"], "values": 173.73926145317662, "errors": 1.7581556087593253, "run_number": 6878, "ndof": 0, "time": "2017-02-08 01:37:20"}},
    {"charge_yield": {"pvalue": 0, "chi2": 0, "names": ["charge_yield"], "values": 425128.5236574601, "errors": 872408.7449313004, "run_number": 6879, "ndof": 0, "time": "2017-02-08 02:37:31"}},
    {"charge_yield": {"pvalue": 0, "chi2": 0, "names": ["charge_yield"], "values": 177.30539413590216, "errors": 4.413550302883247, "run_number": 6880, "ndof": 0, "time": "2017-02-08 03:37:41"}},
    {"charge_yield": {"pvalue": 0, "chi2": 0, "names": ["charge_yield"], "values": 176.64763148123424, "errors": 1.8541438643356785, "run_number": 6881, "ndof": 0, "time": "2017-02-08 04:37:52"}},
    {"charge_yield": {"pvalue": 0, "chi2": 0, "names": ["charge_yield"], "values": -7300.511229226952, "errors": 52.09574793974665, "run_number": 6882, "ndof": 0, "time": "2017-02-08 05:38:03"}},
    {"charge_yield": {"pvalue": 0, "chi2": 0, "names": ["charge_yield"], "values": 195.55868945620827, "errors": 303.93037219545687, "run_number": 6883, "ndof": 0, "time": "2017-02-08 06:38:14"}},
    {"charge_yield": {"pvalue": 0, "chi2": 0, "names": ["charge_yield"], "values": 241.19212121191288, "errors": 58.16616754222684, "run_number": 6884, "ndof": 0, "time": "2017-02-08 07:38:25"}},
    {"charge_yield": {"pvalue": 0, "chi2": 0, "names": ["charge_yield"], "values": 250.88418832119174, "errors": 84.29257119553843, "run_number": 6885, "ndof": 0, "time": "2017-02-08 08:38:36"}},
    {"charge_yield": {"pvalue": 0, "chi2": 0, "names": ["charge_yield"], "values": 172.864061637665, "errors": 13.354295744368448, "run_number": 6886, "ndof": 0, "time": "2017-02-08 09:38:47"}}
]

test = collection.insert_many(entriesJson)

print(test.inserted_ids)
