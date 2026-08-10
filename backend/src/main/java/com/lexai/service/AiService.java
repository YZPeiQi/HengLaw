package com.lexai.service;

import com.lexai.config.SiliconFlowConfig;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.*;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

import java.util.*;

@Service
@RequiredArgsConstructor
@Slf4j
public class AiService {
    
    private final RestTemplate siliconFlowRestTemplate;
    private final SiliconFlowConfig siliconFlowConfig;
    private static final String CONSULTATION_MODEL = "tencent/hunyuan-a13b-instruct";

    private static final String CONSULTATION_PROMPT = """
            你是一位专业的法律顾问。请根据以下问题提供专业的法律建议。

            问题：%s
            咨询类别：%s

            请用通俗易懂的语言解释相关法律条文和应对措施。如果涉及诉讼风险，请明确提示。
            """;

    private static final String CASE_ANALYSIS_PROMPT = """
            你是一位资深法官和法律专家。请分析以下案件：

            案件名称：%s
            案件类型：%s
            案件描述：%s

            请从以下维度进行分析：
            1. 案件争议焦点
            2. 适用的法律条文（列出具体法条）
            3. 各方责任划分
            4. 可能的判决结果
            5. 建议的诉讼策略
            6. 风险等级评估（高/中/低）
            7. 建议的证据准备

            请以JSON格式返回结果。
            """;

    private static final String CONTRACT_REVIEW_PROMPT = """
            你现在是一位经验丰富的合同审查专家。请对以下合同进行全面审查，完成以下任务：

            【任务一：法律效力判断】
            1. 判断本合同是否具有法律效力，从以下三个维度进行分析：
               - 主体资格：签约各方是否具备相应的民事行为能力（自然人是否成年、法人是否合法存续）
               - 意思表示：合同内容是否为双方真实意愿的体现，是否存在欺诈、胁迫或虚假意思表示的情形
               - 内容合法性：合同条款是否违反法律、行政法规的强制性规定，是否违背公序良俗

            2. 如存在可能导致合同无效的情形，请明确指出并说明依据（可引用《民法典》相关规定）。

            【任务二：风险点审查】
            请审查以下内容，指出潜在风险并标注风险等级（高/中/低）：
            - 合同标的约定是否清晰明确（规格、数量、质量标准等）
            - 价款或报酬条款是否合理（金额、支付方式、支付时间、支付条件）
            - 履行期限、地点和方式是否明确可行
            - 违约责任约定是否公平合理、具有可操作性
            - 争议解决条款是否有效（仲裁机构或管辖法院是否明确）

            【任务三：修改建议】
            针对发现的问题，请提供具体的修改建议。（严格不超过80字）

            合同名称：%s
            合同类型：%s
            合同内容：
            %s

            请以JSON格式返回审查结果，包含以下字段：
            - legalEffect: { isValid: boolean, analysis: string（严格不超过80字）, riskLevel: string }
            - riskPoints: [{ clause: string, risk: string, level: string, suggestion: string }]
            - modificationSuggestions: string（严格不超过80字）
            - summary: string（严格不超过80字）
            """;
    
    private static final String CONTRACT_REVIEW_ADVANCED_PROMPT = """
            【角色设定】
            你现在是一位经验丰富的合同审查律师，拥有10年以上合同法实务经验。你的任务是帮助我方审查以下合同，在尽可能保障我方核心利益的同时，促成交易的顺利达成。

            【审查依据】
            请依据《中华人民共和国民法典》合同编及现行有效的司法解释，以及相关行业商业惯例和交易习惯进行审查。

            【合同背景信息】
            - 合同名称：%s
            - 合同类型：%s
            - 合同内容：
            %s

            【核心审查任务】

            一、合同法律效力判断
            请逐项分析本合同是否存在影响法律效力的情形：
            1. 主体资格是否合法（自然人是否具有完全民事行为能力；法人或非法人组织是否依法成立并有效存续）
            2. 意思表示是否真实（是否存在欺诈、胁迫、重大误解或虚假意思表示）
            3. 合同内容是否合法（是否违反法律、行政法规的强制性规定，是否违背公序良俗）
            4. 是否存在其他效力瑕疵情形

            二、合同关键条款审查
            请逐项审查以下条款，指出风险点并提出修改建议：

            1. 合同标的条款 - 标的物/服务内容是否明确具体
            2. 价款与支付条款 - 金额、支付方式、支付时间是否明确
            3. 履行条款 - 履行期限、地点、方式是否合理明确
            4. 违约责任条款 - 违约情形是否明确，责任是否公平合理
            5. 争议解决条款 - 仲裁机构或管辖法院是否明确有效

            三、特殊条款审查
            - 保密条款、知识产权条款、免责条款、格式条款

            【输出格式要求】
            请按以下格式输出：

            ## 一、法律效力判断结论
            [写明合同是否具有法律效力，依据及结论]（严格不超过80字）

            ## 二、风险点汇总表
            | 序号 | 条款位置 | 风险描述 | 风险等级 | 修改建议 |

            ## 三、综合评估与建议
            [综合判断合同的公平性、可执行性，以及是否建议签署]（严格不超过80字）

            请以JSON格式返回，包含以下字段：
            - legalEffect: { isValid: boolean, analysis: string（严格不超过80字）（严格不超过80字）, riskLevel: string }
            - riskPoints: [{ clause: string, risk: string, level: string, suggestion: string }]
            - modificationSuggestions: string（严格不超过80字）
            - summary: string（严格不超过80字）
            """;

    private static final String LABOR_CONTRACT_PROMPT = """
            你现在是一位擅长劳动法的专业律师。请对以下劳动合同进行全面审查，重点分析法律效力及劳动者/用人单位的核心权益风险。

            【法律效力判断】
            1. 签约主体是否适格：用人单位是否合法成立（具有营业执照）；劳动者是否年满16周岁（文艺/体育/特种工艺单位除外），是否具有完全民事行为能力。
            2. 合同内容是否违反《劳动合同法》强制性规定（如：不得约定由劳动者承担违约金（除专项培训服务期和竞业限制外）、不得非法收取押金或扣押证件、不得约定"工伤概不负责"等无效免责条款）。
            3. 是否存在以欺诈、胁迫手段订立的合同。

            【专项审查要点】
            - 合同期限类型：固定期限、无固定期限还是以完成一定工作为期限？是否依法约定试用期（试用期最长6个月，且不得单独约定，试用期工资不得低于转正工资80%或当地最低工资）。
            - 工作内容与地点：是否明确具体（不得写"公司安排的其他工作"过于宽泛）；工作地点是否明确（如多个城市需列举）。
            - 劳动报酬：工资构成（基本工资、绩效、津贴等）是否清晰；支付日期是否明确（至少每月一次）；加班费计算基数是否符合规定。
            - 工作时间与休息休假：标准工时、综合计算工时还是不定时工作制？后两者是否经劳动行政部门审批；年休假、病假等法定假期是否落实。
            - 社会保险与公积金：是否明确约定依法缴纳（口头或书面约定不缴纳属违法）。
            - 解除与终止条款：是否与法定解除条件一致（不得随意增加单位单方解除情形）；经济补偿金计算是否符合《劳动合同法》第47条。
            - 竞业限制：是否限于高管、高技术人员及其他负有保密义务的人员；期限不超过2年；是否约定按月支付经济补偿（不低于劳动合同终止前12个月平均工资的30%且不低于当地最低工资标准）；无补偿的竞业限制条款无效。
            - 违约金条款：除专项培训服务期和竞业限制外，不得约定其他违约金。

            【输出格式】
            请以JSON格式返回，包含以下字段：
            - legalEffect: { isValid: boolean, analysis: string（严格不超过80字）, riskLevel: string }
            - riskPoints: [{ clause: string, risk: string, level: string, suggestion: string }]
            - modificationSuggestions: string
            - summary: string

            合同名称：%s
            合同类型：%s
            合同内容：
            %s
            """;

    private static final String LEASE_CONTRACT_PROMPT = """
            你现在是一位擅长合同法的律师，专注于租赁合同纠纷处理。请对以下租赁合同进行审查。

            【法律效力判断】
            1. 出租人是否有权出租（是否为所有权人/合法转租人）；租赁物是否为法律禁止出租的物品（如违法建筑、未经消防验收的房屋等）。
            2. 租赁期限是否超过20年（超过部分无效）；是否以合法形式掩盖非法目的（如以租代售违规房产）。

            【专项审查要点】
            - 租赁物信息：房屋地址/设备型号及唯一识别码是否准确；面积/规格是否明确；是否有附属设施清单。
            - 租赁用途：是否明确具体（居住/办公/商铺/仓储等），是否符合房屋规划用途。
            - 租金与押金：租金支付周期、递增方式是否清晰；押金数额是否合理（通常不超过3个月租金）；押金退还条件及期限是否明确（不得无故扣押）。
            - 维修责任：出租人的法定维修义务是否被不合理免除（如"一切维修由承租人负责"可能无效）；承租人使用不当造成的损坏责任划分。
            - 转租条款：是否允许转租；若允许，是否需要出租人书面同意；擅自转租的法律后果。
            - 优先购买权与买卖不破租赁：是否明确约定承租人享有优先购买权，且出租人出售时需通知；租赁期内房屋所有权变动不影响租赁合同效力（但需排除例外情形如先抵押后租赁）。
            - 合同解除条件：出租人能否以"自用"为由提前解除（应明确补偿方案）；承租人提前退租的违约责任是否合理（一般不超过1-2个月租金）。
            - 拆迁/不可抗力：遇拆迁或政府行为时，装修补偿、搬迁费归属是否明确。

            【输出格式】
            请以JSON格式返回，包含以下字段：
            - legalEffect: { isValid: boolean, analysis: string（严格不超过80字）, riskLevel: string }
            - riskPoints: [{ clause: string, risk: string, level: string, suggestion: string }]
            - modificationSuggestions: string
            - summary: string

            合同名称：%s
            合同类型：%s
            合同内容：
            %s
            """;

    private static final String PURCHASE_CONTRACT_PROMPT = """
            你现在是一位擅长买卖合同纠纷的律师。请对以下买卖合同进行全面审查。

            【法律效力判断】
            1. 买卖双方是否具有相应的民事行为能力（公司是否处于正常经营状态，个人是否成年）。
            2. 标的物是否合法（禁止买卖违禁品、侵权产品等）；是否存在无权处分（如出卖人并非所有人且未经授权）。
            3. 是否存在虚假意思表示（如名为买卖实为借贷或担保）。

            【专项审查要点】
            - 标的物条款：名称、品牌、规格型号、数量、质量标准（国家标准/行业标准/封样样品）是否明确；包装要求、随附单证（合格证、说明书等）是否约定。
            - 价款与支付：单价、总价、币种、税费承担（增值税由谁承担）；支付方式（一次性/分期/信用证）；支付条件（如验收合格后支付尾款）是否清晰可操作。
            - 交付条款：交付时间（具体日期或期限）、交付地点、交付方式（送货上门/自提/代办托运）；风险转移节点（通常为交付时转移，但可另行约定）。
            - 验收条款：验收期限、验收标准、异议提出方式及期限（隐蔽瑕疵的发现期限）；买方怠于验收的法律后果。
            - 质量保证与售后服务：质保期限、质保范围（是否包括易耗品）、维修响应时间、费用承担；退货/换货/修理的条件。
            - 违约责任：逾期交货/逾期付款的违约金计算标准（不宜过高，超过LPR4倍可被调减）；质量不合格的违约责任；是否约定定金条款（定金不得超过主合同标的额20%，超过部分无效）。
            - 所有权保留：如约定货款付清前所有权不转移，是否明确登记（根据《民法典》第641条，未经登记不得对抗善意第三人）。
            - 争议解决：仲裁机构或法院管辖是否明确且对己方有利。

            【输出格式】
            请以JSON格式返回，包含以下字段：
            - legalEffect: { isValid: boolean, analysis: string（严格不超过80字）, riskLevel: string }
            - riskPoints: [{ clause: string, risk: string, level: string, suggestion: string }]
            - modificationSuggestions: string
            - summary: string

            合同名称：%s
            合同类型：%s
            合同内容：
            %s
            """;

    private static final String LOAN_CONTRACT_PROMPT = """
            你现在是一位精通金融借贷法律的律师。请对以下借款合同进行审查，重点关注民间借贷利率保护上限及合同效力。

            【法律效力判断】
            1. 出借资金是否为自有资金（套取金融机构贷款转贷的，合同无效；职业放贷人（未依法取得放贷资格且以放贷为业的）签订的借款合同无效）。
            2. 借款用途是否合法（用于赌博、贩毒等非法活动的借款合同无效）。
            3. 是否存在"砍头息"（预先在本金中扣除利息，应按实际出借金额认定本金）。

            【专项审查要点】
            - 借款金额与币种：大小写是否一致；是否明确约定本金。
            - 利率与利息：利率是否为年化利率（区分月息/日息）；是否超过法律保护上限（当前LPR的4倍，超过部分法院不予支持）；是否明确利息起算日、结息方式（一次性还本付息/等额本息/等额本金）；是否约定复利（利滚利可能被调整）。
            - 还款方式与期限：还款计划表是否清晰；提前还款是否允许，是否有额外费用或违约金（通常不应收取剩余期限全额利息）。
            - 担保条款（如有）：保证人是否具有代偿能力；抵押/质押是否办理登记（不动产抵押需登记才设立）；担保范围是否包括本金、利息、违约金及实现债权的费用。
            - 违约责任：逾期利率是否超过法定上限（逾期利率+合同期内利率合计不超过LPR4倍）；是否约定罚息及复利。
            - 争议解决条款：注意约定出借方所在地法院管辖对借款人可能不便，可争取借款人住所地或合同履行地法院。
            - 夫妻共同债务：若借款人为自然人，是否要求配偶签字确认（否则可能不认定为夫妻共同债务）。

            【输出格式】
            请以JSON格式返回，包含以下字段：
            - legalEffect: { isValid: boolean, analysis: string（严格不超过80字）, riskLevel: string }
            - riskPoints: [{ clause: string, risk: string, level: string, suggestion: string }]
            - modificationSuggestions: string
            - summary: string

            合同名称：%s
            合同类型：%s
            合同内容：
            %s
            """;

    private static final String SERVICE_CONTRACT_PROMPT = """
            你现在是一位擅长服务合同纠纷的律师。请对以下服务合同（如咨询服务、IT服务、保洁服务、法律服务等）进行审查。

            【法律效力判断】
            1. 服务提供方是否具备法定资质（如：保安服务需《保安服务许可证》、建筑服务需相应资质等）；若欠缺资质，合同可能无效或导致行政处罚。
            2. 服务内容是否违反公序良俗或强制性规定。

            【专项审查要点】
            - 服务范围与标准：服务内容、交付成果（报告/系统/服务行为）是否具体可衡量；验收标准是否客观（避免"满意""认可"等主观表述）；服务水平协议（SLA）中关键绩效指标（KPI）是否明确。
            - 服务期限与地点：服务起止时间、工作地点、服务频次（如每周一次）是否明确。
            - 费用与支付：总价或计费方式（按人天/按项目/按效果）；支付节点是否与交付成果挂钩（如验收合格后支付尾款）；是否包含差旅费、材料费等额外费用。
            - 人员安排：是否指定核心服务人员；更换人员是否需要甲方同意。
            - 知识产权：服务过程中产生的成果（报告、代码、设计图等）归属哪一方；如归甲方，需明确约定"知识产权归甲方所有，乙方不得另作他用"；背景知识产权许可范围是否明确。
            - 保密条款：保密信息范围、保密期限（可约定到期后仍保密）、违约责任。
            - 转分包限制：是否允许服务方将工作转包或分包给第三方；若允许，是否要求第三方签署同等保密协议并承担责任。
            - 违约责任与解除权：服务质量不达标的补救措施（整改、扣减费用、解除合同）；一方拖延履行时另一方的单方解除权；解除后的结算与资料返还。

            【输出格式】
            请以JSON格式返回，包含以下字段：
            - legalEffect: { isValid: boolean, analysis: string（严格不超过80字）, riskLevel: string }
            - riskPoints: [{ clause: string, risk: string, level: string, suggestion: string }]
            - modificationSuggestions: string
            - summary: string

            合同名称：%s
            合同类型：%s
            合同内容：
            %s
            """;

    private static final String TECH_CONTRACT_PROMPT = """
            你现在是一位擅长技术合同与知识产权法律的律师。请对以下技术合同进行审查，注意区分合同类型（开发/转让/许可/咨询/服务）。

            【法律效力判断】
            1. 技术是否属于国家限制或禁止进出口/转移的范围；涉及国家安全或重大利益的技术，未经批准合同可能无效。
            2. 非法垄断技术、妨碍技术进步（如限制另一方从其他渠道获取技术）的条款无效（《技术合同司法解释》第10条）。

            【专项审查要点（按合同类型侧重）】

            A. 技术开发合同（委托开发/合作开发）
            - 研发目标与验收标准：技术指标、功能需求是否具体可验证（避免"先进水平"等模糊词）；验收方式、验收期限。
            - 研发计划与经费：经费总额、分担方式、支付节点；研发风险由谁承担（无约定则委托方承担全部风险）；合理约定"风险条款"而非包揽成功。
            - 知识产权归属：
              * 委托开发：申请专利的权利归研究开发人，但委托人可免费实施该专利（另有约定除外）；若委托人希望取得专利权，需明确约定。
              * 合作开发：申请专利的权利归合作各方共有，一方转让需另一方同意。
              * 软件著作权：应明确归属，否则可能按委托作品认定归受托人。
            - 后续改进成果：一方在合同成果基础上独立改进的技术，归属改进方；但可约定相互免费许可使用。

            B. 技术转让与许可合同
            - 转让或许可的类型：独占/排他/普通许可；地域范围、期限、能否分许可。
            - 技术资料交付与技术服务：是否提供技术文档、培训、安装调试等。
            - 侵权责任：如转让的技术侵犯第三方知识产权，转让方承担全部责任。
            - 改进技术的归属：同上述后续改进规则。

            C. 通用要点
            - 保密条款：技术秘密的保密措施、保密期限、解密条件。
            - 验收与质保：技术实施后是否符合约定效果；质保期内的维护义务。
            - 付款方式：入门费+提成（提成比例、销售额计算方式、审计权）。

            【输出格式】
            请以JSON格式返回，包含以下字段：
            - legalEffect: { isValid: boolean, analysis: string（严格不超过80字）, riskLevel: string }
            - riskPoints: [{ clause: string, risk: string, level: string, suggestion: string }]
            - modificationSuggestions: string
            - summary: string

            合同名称：%s
            合同类型：%s
            合同内容：
            %s
            """;

    private static final String INVEST_CONTRACT_PROMPT = """
            你现在是一位精通投融资与公司法的律师。请对以下投资合同进行审查，关注交易结构合法性及投资者保护条款。

            【法律效力判断】
            1. 目标公司是否合法存续；增资/股权转让是否履行内部决议程序（股东会/董事会决议）；涉及国有资产是否经评估及国资监管部门批准。
            2. 是否存在违反《公司法》强制性规定的情形（如：股份有限公司同股同权原则的限制、优先股发行须符合规定）。
            3. 对赌协议（估值调整条款）是否有效：根据《九民纪要》，投资方与目标公司对赌，须审查是否完成减资程序（否则无效）；与股东对赌一般有效。

            【专项审查要点】
            - 投资金额与估值：投前估值、投后估值；投资款用途是否限定（不得用于非经营性支出）。
            - 股权/份额安排：投资方获得的股权比例、优先股/普通股类型；表决权、分红权、剩余财产分配权是否与持股比例一致（有无特殊约定如优先分红、一票否决权）。
            - 股东协议特殊权利：
              * 优先认购权、优先购买权、共同出售权、拖售权（领售权）
              * 反稀释条款（完全棘轮/加权平均）
              * 业绩承诺与补偿（对赌）
              * 回购权（触发条件如未在约定时间内上市，回购价格计算方式）
              * 清算优先权（如投资方优先拿回本金及固定回报）
            - 公司治理：董事会席位、一票否决权事项范围（重大资产处置、增资、修改章程等）；信息检查权。
            - 陈述与保证：目标公司及原股东对财务、资产、知识产权、诉讼、税务等状况的真实性保证；违反陈述与保证的赔偿责任。
            - 交割条件：先决条件（尽职调查满意、股东会批准，政府审批等）；交割后义务。
            - 退出机制：上市、并购、回购、清算等退出路径及各方权利义务。

            【输出格式】
            请以JSON格式返回，包含以下字段：
            - legalEffect: { isValid: boolean, analysis: string（严格不超过80字）, riskLevel: string }
            - riskPoints: [{ clause: string, risk: string, level: string, suggestion: string }]
            - modificationSuggestions: string
            - summary: string

            合同名称：%s
            合同类型：%s
            合同内容：
            %s
            """;

    private static final String GENERAL_CONTRACT_PROMPT = """
            你现在是一位经验丰富的合同律师。请对以下这份合同进行审查，运用一般合同法的基本原则。

            【法律效力判断】
            根据《民法典》第143条至157条，判断：
            - 主体是否适格（自然人/法人/非法人组织）
            - 意思表示是否真实
            - 内容是否违反法律强制性规定或公序良俗

            【通用审查框架】（适用于任何无名合同）
            请按以下维度逐项审查：
            1. 合同标的条款：是否明确、合法、可能（标的物/行为/权利）
            2. 数量与质量：是否具体可衡量
            3. 价款或报酬：金额、支付方式、支付条件是否清晰
            4. 履行条款：期限、地点、方式是否确定
            5. 违约责任：是否对等、合理、可执行
            6. 争议解决：管辖约定是否明确有效
            7. 特别条款：根据合同性质（如合作、承揽、运输、保管等）参照最相类似的有名合同规则审查（如《民法典》第467条）

            【输出格式】
            请以JSON格式返回，包含以下字段：
            - legalEffect: { isValid: boolean, analysis: string（严格不超过80字）, riskLevel: string }
            - riskPoints: [{ clause: string, risk: string, level: string, suggestion: string }]
            - modificationSuggestions: string
            - summary: string

            合同名称：%s
            合同类型：%s
            合同内容：
            %s
            """;

    private static final String DOCUMENT_GENERATION_PROMPT = """
            你是一位专业的法律文书撰写专家。请根据以下信息生成法律文书：

            文书类型：%s
            标题：%s
            原告/甲方信息：%s
            被告/乙方信息：%s
            案件描述：%s
            诉讼请求：%s

            请生成一份完整、规范的法律文书，包括：
            1. 规范的文书格式
            2. 准确的法律用语
            3. 完整的必要条款

            直接返回文书内容，不要添加其他解释。
            """;

    public String consultation(String question, String category, String model) {
        String prompt = String.format(CONSULTATION_PROMPT, question, category != null ? category : "综合");
        return sanitizeAiText(chat(prompt, CONSULTATION_MODEL));
    }

    public Map<String, Object> analyzeCase(String caseName, String caseType, String description) {
        String prompt = String.format(CASE_ANALYSIS_PROMPT, caseName, caseType, description);
        String result = chat(prompt, null);
        return parseJsonResponse(result);
    }

    public Map<String, Object> reviewContract(String contractName, String contractType, String content, String reviewMode) {
        String prompt = selectPromptByType(contractName, contractType, content, reviewMode);
        String result = chat(prompt, null);
        return parseJsonResponse(result);
    }

    private String selectPromptByType(String contractName, String contractType, String content, String reviewMode) {
        boolean isAdvanced = "advanced".equals(reviewMode);

        return switch (contractType) {
            case "劳动合同" -> isAdvanced
                ? String.format(CONTRACT_REVIEW_ADVANCED_PROMPT, contractName, contractType, content)
                : String.format(LABOR_CONTRACT_PROMPT, contractName, contractType, content);
            case "租赁合同" -> isAdvanced
                ? String.format(CONTRACT_REVIEW_ADVANCED_PROMPT, contractName, contractType, content)
                : String.format(LEASE_CONTRACT_PROMPT, contractName, contractType, content);
            case "买卖合同" -> isAdvanced
                ? String.format(CONTRACT_REVIEW_ADVANCED_PROMPT, contractName, contractType, content)
                : String.format(PURCHASE_CONTRACT_PROMPT, contractName, contractType, content);
            case "借款合同" -> isAdvanced
                ? String.format(CONTRACT_REVIEW_ADVANCED_PROMPT, contractName, contractType, content)
                : String.format(LOAN_CONTRACT_PROMPT, contractName, contractType, content);
            case "服务合同" -> isAdvanced
                ? String.format(CONTRACT_REVIEW_ADVANCED_PROMPT, contractName, contractType, content)
                : String.format(SERVICE_CONTRACT_PROMPT, contractName, contractType, content);
            case "技术合同" -> isAdvanced
                ? String.format(CONTRACT_REVIEW_ADVANCED_PROMPT, contractName, contractType, content)
                : String.format(TECH_CONTRACT_PROMPT, contractName, contractType, content);
            case "投资合同" -> isAdvanced
                ? String.format(CONTRACT_REVIEW_ADVANCED_PROMPT, contractName, contractType, content)
                : String.format(INVEST_CONTRACT_PROMPT, contractName, contractType, content);
            default -> isAdvanced
                ? String.format(CONTRACT_REVIEW_ADVANCED_PROMPT, contractName, contractType, content)
                : String.format(GENERAL_CONTRACT_PROMPT, contractName, contractType, content);
        };
    }

    public String generateDocument(String docType, String title, String partyA, String partyB,
                                   String caseDescription, String claim) {
        String prompt = String.format(DOCUMENT_GENERATION_PROMPT,
                docType, title != null ? title : "", partyA, partyB,
                caseDescription != null ? caseDescription : "", claim != null ? claim : "");
        return sanitizeAiText(chat(prompt, CONSULTATION_MODEL));
    }

    public String chat(String prompt, String model) {
        try {
            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_JSON);
            headers.setBearerAuth(siliconFlowConfig.getApiKey());

            Map<String, Object> requestBody = new HashMap<>();
            String selectedModel = (model != null && !model.isBlank()) ? model : siliconFlowConfig.getModel();
            requestBody.put("model", selectedModel);
            requestBody.put("stream", false);

            List<Map<String, String>> messages = new ArrayList<>();
            messages.add(Map.of("role", "user", "content", prompt));
            requestBody.put("messages", messages);

            HttpEntity<Map<String, Object>> entity = new HttpEntity<>(requestBody, headers);

            ResponseEntity<Map> response = siliconFlowRestTemplate.exchange(
                    siliconFlowConfig.getBaseUrl() + "/chat/completions",
                    HttpMethod.POST,
                    entity,
                    Map.class
            );

            if (response.getStatusCode() == HttpStatus.OK && response.getBody() != null) {
                Map<String, Object> body = response.getBody();
                List<Map<String, Object>> choices = (List<Map<String, Object>>) body.get("choices");
                if (choices != null && !choices.isEmpty()) {
                    Map<String, Object> message = (Map<String, Object>) choices.get(0).get("message");
                    return (String) message.get("content");
                }
            }
            return "AI服务暂时无法响应，请稍后再试。";
        } catch (Exception e) {
            log.error("调用AI服务失败", e);
            return "AI服务调用失败：" + e.getMessage();
        }
    }

    private Map<String, Object> parseJsonResponse(String response) {
        Map<String, Object> result = new HashMap<>();
        try {
            if (response.contains("```json")) {
                response = response.substring(response.indexOf("```json") + 7);
                response = response.substring(0, response.indexOf("```"));
            } else if (response.contains("```")) {
                response = response.substring(response.indexOf("```") + 3);
                response = response.substring(0, response.indexOf("```"));
            }
            response = response.trim();

            ObjectMapper mapper = new ObjectMapper();
            result = mapper.readValue(response, Map.class);
        } catch (Exception e) {
            log.warn("解析JSON响应失败，返回原始文本", e);
            result.put("content", response);
            result.put("raw", true);
        }
        return result;
    }

    private String sanitizeAiText(String text) {
        if (text == null || text.isBlank()) {
            return text;
        }

        String cleaned = text;

        // Remove markdown code fences first to avoid leaking wrapper syntax.
        cleaned = cleaned.replace("```json", "");
        cleaned = cleaned.replace("```", "");

        // Remove common markdown formatting artifacts.
        cleaned = cleaned.replace("**", "");
        cleaned = cleaned.replace("__", "");
        cleaned = cleaned.replace("`", "");

        // Drop heading markers at line starts while preserving line content.
        cleaned = cleaned.replaceAll("(?m)^\\s{0,3}#{1,6}\\s*", "");

        // Drop markdown list markers that are often shown as garbled stars on the page.
        cleaned = cleaned.replaceAll("(?m)^\\s{0,3}[*+-]\\s+", "");
        cleaned = cleaned.replaceAll("(?m)^\\s{0,3}\\d+[.)]\\s+", "");

        // Remove standalone star wrappers like *标题* produced by some models.
        cleaned = cleaned.replaceAll("(?m)^\\s*\\*([^*\\r\\n]+)\\*\\s*$", "$1");

        // Remove common garbled/replacement and zero-width characters.
        cleaned = cleaned.replace("\uFFFD", "");
        cleaned = cleaned.replaceAll("[\\u200B-\\u200D\\uFEFF]", "");

        // Normalize trailing spaces and excessive blank lines.
        cleaned = cleaned.replaceAll("[ \\t]+(?=\\r?\\n)", "");
        cleaned = cleaned.replaceAll("(\\r?\\n){3,}", "\n\n");

        return cleaned.trim();
    }

    private static class ObjectMapper {
        public <T> T readValue(String json, Class<T> clazz) throws com.fasterxml.jackson.core.JsonProcessingException {
            return new com.fasterxml.jackson.databind.ObjectMapper().readValue(json, clazz);
        }
    }
}
