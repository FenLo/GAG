const { SlashCommandBuilder, EmbedBuilder } = require('discord.js');

module.exports = {
    data: new SlashCommandBuilder()
        .setName('userinfo')
        .setDescription('Bir kullanıcının bilgilerini görüntüler.')
        .addUserOption(option =>
            option.setName('member')
                .setDescription('Bilgisi görüntülenecek kullanıcı')
                .setRequired(true)),
    async execute(interaction) {
        const member = interaction.options.getMember('member');

        if (!member) {
            return await interaction.reply({ content: '❌ Kullanıcı bulunamadı.', ephemeral: true });
        }

        const roles = member.roles.cache
            .filter(role => role.id !== interaction.guild.id)
            .map(role => role.toString())
            .join(', ') || 'Rol yok';

        const embed = new EmbedBuilder()
            .setColor('#0099ff')
            .setTitle(`👤 ${member.user.tag} - Kullanıcı Bilgileri`)
            .setThumbnail(member.user.displayAvatarURL({ dynamic: true }))
            .addFields(
                { name: '🆔 Kullanıcı ID', value: member.id, inline: true },
                { name: '📝 Takma Ad', value: member.displayName, inline: true },
                { name: '🤖 Bot mu?', value: member.user.bot ? 'Evet' : 'Hayır', inline: true },
                { name: '📅 Hesap Oluşturma', value: member.user.createdAt.toLocaleDateString('tr-TR'), inline: true },
                { name: '📥 Sunucuya Katılma', value: member.joinedAt?.toLocaleDateString('tr-TR') || 'Bilinmiyor', inline: true },
                { name: '🎭 Roller', value: roles, inline: false }
            )
            .setFooter({ text: `Durum: ${member.presence?.status || 'Çevrimdışı'}` })
            .setTimestamp();

        await interaction.reply({ embeds: [embed] });
    }
};
